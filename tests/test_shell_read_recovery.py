"""A failed Git worktree inspection is a read failure, not an unknown write."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import test_jarvis_loop as baseline

loop = baseline.loop
RESULT = 'Exit code: 128\n--- stdout ---\n\n--- stderr ---\nfatal: not a git repository (or any of the parent directories): .git\n'


class ReadOnlyShellTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_observed_command_and_explicit_checkout_are_read_only(self):
        for command in ['cd /home/pagi/breachline-agent && git worktree list',
                        'git -C /home/pagi/breachline-agent/repo worktree list --porcelain',
                        'git --no-optional-locks -C /project/repo worktree list',
                        'git rev-parse --show-toplevel']:
            with self.subTest(command=command):
                args={'command':command}
                self.assertTrue(loop.read_only_shell(args))
                self.assertFalse(loop.potential_write('shell_exec',{'arguments':args}))

    def test_fail_closed_for_mixed_mutating_or_dynamic_shell_commands(self):
        for command in ['git worktree add /game', 'git worktree remove /game',
                        'git -c alias.x=anything worktree list',
                        'cd /project && git worktree list && touch /tmp/side-effect',
                        'git worktree list; touch /tmp/side-effect', 'git worktree list > /tmp/output',
                        'git -C $(touch /tmp/side-effect) worktree list',
                        'git worktree list | tee /tmp/output', 'cd /project && mkdir new && git worktree list',
                        'git worktree list\ntouch /tmp/side-effect', 'echo git worktree list',
                        'git -C "$PROJECT" worktree list', 'git worktree list --output=/tmp/output']:
            with self.subTest(command=command):
                self.assertFalse(loop.read_only_shell({'command':command}))
        self.assertFalse(loop.read_only_shell('{invalid json'))

    def test_current_failed_read_retains_failure_and_allows_next_inference(self):
        ledger=loop.ActionLedger(self.root)
        ledger.record('tool_call_start',{'tool':'shell_exec','arguments':{'command':'cd /project && git worktree list'}})
        ledger.record('tool_call_end',{'tool':'shell_exec','success':False,'returncode':128,'result':RESULT})
        self.assertEqual(ledger.actions[0]['status'],'FAILED')
        self.assertFalse(ledger.actions[0]['potential_write'])
        ledger.check()

    def test_failed_mutating_shell_remains_blocked(self):
        ledger=loop.ActionLedger(self.root)
        ledger.record('tool_call_start',{'tool':'shell_exec','arguments':{'command':'mkdir new; git worktree list'}})
        ledger.record('tool_call_end',{'tool':'shell_exec','success':False,'returncode':128,'result':RESULT})
        with self.assertRaises(loop.UnsafeRecoveryError):
            ledger.check()

    def old_failure(self, command='cd /project && git worktree list', status='FAILED'):
        run=self.root/'runs/20261012-read-failure'
        run.mkdir(parents=True)
        result=run/'tool-result.txt'
        result.write_text(RESULT)
        actions=[{'tool':'shell_exec','status':status,'potential_write':True,'returncode':128,'result_path':str(result)}]
        loop.save_json(run/'manifest.json',{'status':'FAILED','mission_id':'fresh'})
        loop.save_json(run/'action_receipts.json',actions)
        loop.save_json(run/'failure_snapshot.json',{'messages':[
            {'role':'assistant','tool_calls':[{'id':'read-1','name':'shell_exec','arguments':json.dumps({'command':command})}]},
            {'role':'tool','tool_call_id':'read-1','content':RESULT}], 'actions':actions})
        return run

    def test_existing_failure_recovers_with_original_receipts_unchanged(self):
        run=self.old_failure()
        original=(run/'action_receipts.json').read_bytes()
        loop.check_previous_run(self.root)
        self.assertEqual((run/'action_receipts.json').read_bytes(),original)
        review=json.loads((run/'read_only_action_review.json').read_text())
        self.assertEqual(review['actions'][0]['status'],'FAILED')
        self.assertFalse(review['actions'][0]['potential_write'])
        self.assertEqual(review['original_receipts_sha256'],loop.digest(original))
        notice=loop.previous_run_notice(self.root,'fresh')
        self.assertIn('read-only Git failure review',notice)
        self.assertIn('git -C <workspace>/repo',notice)

    def test_existing_write_failure_is_never_reclassified(self):
        self.old_failure('mkdir new && git worktree list')
        with self.assertRaises(loop.UnsafeRecoveryError):
            loop.check_previous_run(self.root)

    def test_missing_or_mismatched_result_stays_blocked(self):
        run=self.old_failure()
        (run/'tool-result.txt').write_text('different result')
        with self.assertRaises(loop.UnsafeRecoveryError):
            loop.check_previous_run(self.root)

    def test_pending_action_stays_blocked_even_with_a_snapshot(self):
        self.old_failure(status='PENDING')
        with self.assertRaises(loop.UnsafeRecoveryError):
            loop.check_previous_run(self.root)


if __name__=='__main__':
    unittest.main()
