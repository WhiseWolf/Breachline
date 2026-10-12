"""Acceptance tests for the defects demonstrated in the 2026-10-12 audit."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch
import test_jarvis_loop as baseline

loop = baseline.loop
spec = importlib.util.spec_from_file_location('private_upload', Path(__file__).parents[1] / 'runtime/upload_private_logs.py')
upload = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upload)


class FakeShell:
    def execute(self, **params):
        return NS(content='Exit code: 255\n--- stdout ---\n\n--- stderr ---\nfatal: branch exists',
                  success=True, metadata={'returncode': 0})


class ProgressGuardTests(unittest.TestCase):
    setUp = baseline.ContextTests.setUp
    write_contract = baseline.ContextTests.write_contract

    def run_dir(self):
        run = self.root / 'logs/runs/current'
        run.mkdir(parents=True)
        return run

    def test_runtime_checkpoint_never_advances_functional_task(self):
        path = self.root / 'logs/CURRENT_WORK.md'
        before = loop.functional_work(path)
        recorder = loop.RecordingEngine(NS(), self.run_dir(), 49152, 2048)
        recorder.anchor_count = 1
        recorder.checkpoint([NS(role='user', content='rules')], 'periodic')
        self.assertEqual(loop.functional_work(path), before)
        self.assertIn('SCHEDULER_CHECKPOINT', path.read_text())

    def test_roll_retains_latest_completed_exchange_and_receipt_target(self):
        run = self.run_dir()
        ledger = loop.ActionLedger(run)
        ledger.record('tool_call_start', {'tool': 'file_write', 'arguments': {'path': '/game/index.html'}})
        ledger.record('tool_call_end', {'tool': 'file_write', 'success': True, 'result_path': str(run / 'result.txt')})
        recorder = loop.RecordingEngine(NS(), run, 49152, 2048, ledger=ledger)
        recorder.anchor_count = 1
        messages = [NS(role='user', content='rules'),
                    NS(role='assistant', content='previous', tool_calls=[{'id':'old'}]),
                    NS(role='tool', content='old data', tool_call_id='old'),
                    NS(role='assistant', content='write it', tool_calls=[{'id':'new'}]),
                    NS(role='tool', content='UNIQUE_SUCCESS /game/index.html', tool_call_id='new')]
        self.assertTrue(recorder.roll_history(messages, 'test'))
        self.assertEqual(messages[-1].content, 'UNIQUE_SUCCESS /game/index.html')
        self.assertEqual(messages[-2].tool_calls, [{'id':'new'}])
        self.assertIn('/game/index.html', messages[1].content)
        self.assertEqual(messages[0].content, 'rules')

    def test_sole_exchange_is_not_removed(self):
        recorder = loop.RecordingEngine(NS(), self.run_dir(), 49152, 2048)
        recorder.anchor_count = 1
        messages = [NS(role='user', content='rules'), NS(role='assistant', content='read', tool_calls=[{'id':'a'}]),
                    NS(role='tool', content='LAST RESULT', tool_call_id='a')]
        self.assertFalse(recorder.roll_history(messages, 'test'))
        self.assertEqual(messages[-1].content, 'LAST RESULT')

    def test_calibration_keeps_large_unchanged_prefix_and_small_history(self):
        engine = NS(generate=Mock(return_value={'content':'continue', 'usage':{'prompt_tokens':21000}}))
        recorder = loop.RecordingEngine(engine, self.run_dir(), 49152, 2048)
        messages = [NS(role='user', content='R' * 85000)]
        recorder.generate(messages)
        for i in range(6):
            messages += [NS(role='assistant', content='inspect', tool_calls=[{'id':str(i)}]),
                         NS(role='tool', content='small result', tool_call_id=str(i))]
            recorder.generate(messages)
        self.assertEqual(len(messages), 13)
        self.assertEqual(messages[0].content, 'R' * 85000)
        events = (recorder.run_dir / 'recovery.jsonl').read_text()
        self.assertNotIn('CONTEXT_ROLL', events)

    def test_changed_prefix_invalidates_calibration_and_oversize_still_blocks(self):
        recorder = loop.RecordingEngine(NS(generate=Mock(return_value={'usage':{'prompt_tokens':50}})), self.run_dir(), 32768, 2048)
        recorder.generate([NS(role='user', content='small')])
        with self.assertRaises(loop.ContextBudgetError):
            recorder.generate([NS(role='user', content='X' * 120000)])

    def test_compaction_never_expands_short_outputs(self):
        recorder = loop.RecordingEngine(NS(), self.run_dir(), 49152, 2048)
        message = NS(role='tool', content='x' * 200, tool_call_id='a')
        self.assertIs(recorder.compact_outputs([message], 128)[0], message)

    def test_nonzero_shell_header_overrules_false_success(self):
        ledger = loop.ActionLedger(self.run_dir())
        ledger.record('tool_call_start', {'tool':'shell_exec'})
        ledger.record('tool_call_end', {'tool':'shell_exec','success':True,'returncode':0,
                                      'result':'Exit code: 255\n--- stdout ---\n\n--- stderr ---\nfatal'})
        self.assertEqual(ledger.actions[0]['status'], 'FAILED')
        self.assertEqual(ledger.actions[0]['returncode'], 255)
        with self.assertRaises(loop.UnsafeRecoveryError):
            ledger.check()

    def test_shell_guard_uses_existing_tool_and_restores_it(self):
        original = FakeShell.execute
        modules = {'openjarvis.core.registry':NS(ToolRegistry=NS(get=lambda name: FakeShell))}
        with patch.dict(sys.modules, modules), patch.object(loop, 'control_checkout', return_value={}):
            restore = loop.install_shell_guard(self.root)
            result = FakeShell().execute(command='git worktree add anything')
            self.assertFalse(result.success)
            self.assertEqual(result.metadata['returncode'], 255)
            restore()
        self.assertIs(FakeShell.execute, original)

    def test_game_slug_named_checkout_does_not_block_a_git_read(self):
        original=FakeShell.execute
        modules={'openjarvis.core.registry':NS(ToolRegistry=NS(get=lambda name:FakeShell))}
        with patch.dict(sys.modules,modules), patch.object(loop,'control_checkout',return_value={}):
            restore=loop.install_shell_guard(self.root)
            try:
                result=FakeShell().execute(command='git diff games/checkout/index.html')
                self.assertNotIn('policy blocked',result.content)
            finally:
                restore()
        self.assertIs(FakeShell.execute,original)

    def test_artifact_snapshot_includes_preferred_game_worktree(self):
        game=self.root/'worktrees/puzzle/games/puzzle/index.html'
        game.parent.mkdir(parents=True)
        game.write_text('prototype')
        self.assertIn('worktrees/puzzle/games/puzzle/index.html',loop.artifact_snapshot(self.root))

    def test_branch_switch_is_blocked_before_original_execution(self):
        calls = Mock(return_value=NS())
        modules = {'openjarvis.core.registry':NS(ToolRegistry=NS(get=lambda name: FakeShell)),
                   'openjarvis.core.types':NS(ToolResult=lambda **kwargs:NS(**kwargs))}
        with patch.object(FakeShell, 'execute', calls), patch.dict(sys.modules, modules), \
             patch.object(loop,'control_checkout',return_value={}):
            restore = loop.install_shell_guard(self.root)
            try:
                result = FakeShell().execute(command='git -C /control switch other')
                self.assertFalse(result.success)
                self.assertTrue(loop.failed_before_execution('shell_exec', result.content))
                calls.assert_not_called()
            finally:
                restore()

    def test_control_checkout_reads_real_git_state_and_never_resets(self):
        repo = self.root / 'repo'
        subprocess.run(['git','init','-q','-b','agent-lab',str(repo)],check=True)
        self.assertEqual(loop.control_checkout(self.root)['branch'],'agent-lab')
        subprocess.run(['git','-C',str(repo),'symbolic-ref','HEAD','refs/heads/game/drift'],check=True)
        with self.assertRaisesRegex(RuntimeError,'agent-lab'):
            loop.control_checkout(self.root)
        self.assertEqual(subprocess.check_output(['git','-C',str(repo),'symbolic-ref','--short','HEAD'],text=True).strip(),'game/drift')

    def test_private_log_copy_excludes_git_database_but_keeps_every_run(self):
        logs = self.root / 'logs'
        (logs / '.git/objects').mkdir(parents=True)
        (logs / '.git/objects/binary').write_bytes(b'\xff\xfe')
        (logs / 'runs/old').mkdir(parents=True)
        (logs / 'runs/old/checkpoint.json').write_text('{"message":"FULL DATA"}')
        with patch.object(upload,'known_secrets',return_value=set()):
            copied = upload.copy_logs(logs,self.root/'copy')
        self.assertFalse((self.root/'copy/.git').exists())
        self.assertTrue(any(x['path']=='runs/old/checkpoint.json' for x in copied))

    def test_stored_credentials_masked_without_altering_execution_object(self):
        token = 'ghp_' + 'x' * 30
        obj = {'access_token':token,'content':'Bearer '+token,'tool_calls':[{'id':'a','arguments':json.dumps({'api_key':token})}]}
        target = self.root / 'evidence.json'
        loop.save_json(target,obj)
        self.assertNotIn(token,target.read_text())
        self.assertEqual(obj['access_token'],token)
        self.assertIn('"id": "a"',target.read_text())

    def test_briefing_sync_preserves_logs_and_unrecognized_edits(self):
        spec = importlib.util.spec_from_file_location('sync_brief', Path(__file__).parents[1] / 'runtime/sync_briefing.py')
        sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync)
        repo = self.root / 'repo'
        (repo / 'briefing').mkdir(parents=True)
        (repo / 'briefing/update.md').write_text('new rules')
        active = self.root / 'briefing/update.md'
        active.write_text('old rules')
        expected = loop.digest(active.read_bytes())
        logs_before = (self.root / 'logs/CURRENT_WORK.md').read_bytes()
        with patch.object(sync,'BASELINE',{'update.md':expected}):
            result=sync.sync(repo,self.root)
            self.assertEqual(result['status'],'UPDATED')
            self.assertEqual(active.read_text(),'new rules')
            self.assertEqual((Path(result['backup'])/'update.md').read_text(),'old rules')
            active.write_text('unrecognized local work')
            with self.assertRaisesRegex(SystemExit,'nichts überschrieben'):
                sync.sync(repo,self.root)
            self.assertEqual(active.read_text(),'unrecognized local work')
        self.assertEqual((self.root/'logs/CURRENT_WORK.md').read_bytes(),logs_before)

    def test_two_cycles_carry_actual_artifact_and_require_missing_handoff(self):
        cfg = NS(agent=NS(max_turns=60), intelligence=NS(max_tokens=2048,temperature=.3))
        engine = NS(generate=Mock(return_value={'content':'ok'}),close=Mock())
        observed=[]
        class Bus:
            def __init__(self): self.callbacks={}
            def subscribe(self,kind,callback): self.callbacks[kind.value]=callback
            def emit(self,kind,**data): self.callbacks[kind](NS(event_type=NS(value=kind),data=data))
        def agent(**kwargs):
            observed.append(kwargs['query_text'])
            messages=[NS(role='user',content=kwargs['query_text'])]
            kwargs['engine'].generate(messages)
            game=self.root/'games/quickpuzzle/index.html'
            tool='file_write' if len(observed)==1 else 'file_read'
            if len(observed)==1:
                game.parent.mkdir(parents=True)
                game.write_text('actual prototype')
            else:
                self.assertEqual(game.read_text(),'actual prototype')
                (self.root/'logs/CURRENT_WORK.md').write_text('Existing prototype verified. NEXT: test gameplay.')
            bus=kwargs['bus']
            bus.emit('tool_call_start',tool=tool,arguments={'path':str(game)})
            bus.emit('tool_call_end',tool=tool,success=True,result='actual prototype')
            return NS(content='done',turns=1,metadata={},tool_results=[NS(tool_name=tool,success=True,content='actual prototype',metadata={'path':str(game)})])
        modules={'openjarvis.core.events':NS(EventBus=Bus,EventType=NS(TOOL_CALL_START=NS(value='tool_call_start'),TOOL_CALL_END=NS(value='tool_call_end'))),
                 'openjarvis.engine':NS(get_engine=lambda *args:('ollama',engine)),
                 'openjarvis.security':NS(setup_security=lambda *args:NS(engine=engine)),
                 'openjarvis.cli.ask':NS(_run_agent=agent)}
        config=self.root/'config.toml'
        config.write_text('existing config')
        with patch.dict(sys.modules,modules), patch.object(loop,'prepare_runtime',return_value=(cfg,'operative','local',['file_write','file_read'],[])), \
             patch.object(loop,'control_checkout',return_value={'branch':'agent-lab'}), \
             patch.object(loop,'install_shell_guard',return_value=lambda:None), patch.object(loop,'isolated_docker_proof',return_value=None):
            first=loop.run_cycle(self.root,config,self.prompt,49152)
            second=loop.run_cycle(self.root,config,self.prompt,49152)
        self.assertEqual(first,'HANDOFF_REQUIRED')
        self.assertEqual(second,'CYCLE_RETURNED')
        self.assertIn('games/quickpuzzle/index.html',observed[1])
        self.assertIn('CURRENT RECOVERY TASK',observed[1])
        self.assertEqual(config.read_text(),'existing config')


if __name__=='__main__':
    unittest.main()
