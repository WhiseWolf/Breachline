(function(root){
'use strict';
const W=960,H=640;
function create(){return {time:0,wave:0,nextWave:0,spawn:0,remaining:0,kills:0,dead:false,upgrade:false,upgrades:0,player:{x:480,y:320,hp:100,inv:0,cool:0,angle:0,damage:1,interval:.32},enemies:[],shots:[],id:0};}
function step(s,input,dt,random=Math.random){
 if(s.dead||s.upgrade)return;s.time+=dt;
 const p=s.player;p.inv=Math.max(0,p.inv-dt);p.cool-=dt;
 let dx=input.x||0,dy=input.y||0,len=Math.hypot(dx,dy);if(len>1){dx/=len;dy/=len;}
 p.x=Math.max(20,Math.min(W-20,p.x+dx*205*dt));p.y=Math.max(20,Math.min(H-20,p.y+dy*205*dt));
 if(s.time>=s.nextWave){s.wave++;s.remaining+=9+s.wave*3;s.nextWave=s.time+20;s.spawn=0;if(s.wave%2===0){s.upgrade=true;return;}}
 s.spawn-=dt;
 if(s.remaining&&s.spawn<=0&&s.enemies.length<100){const side=Math.floor(random()*4),t=random(),roll=random(),kind=s.wave>=3&&roll<.2?'brute':s.wave>=2&&roll<.5?'runner':'walker';s.enemies.push({id:++s.id,x:side===0?-18:side===1?W+18:t*W,y:side===2?-18:side===3?H+18:t*H,kind,hp:kind==='brute'?9:kind==='runner'?2:3,r:kind==='brute'?20:13,speed:kind==='runner'?Math.min(215,135+s.wave*5):kind==='brute'?Math.min(115,38+s.wave*4):Math.min(155,48+s.wave*7),angle:0});s.remaining--;s.spawn=Math.max(.18,.6-s.wave*.035);}
 let target=null,best=310;
 for(const e of s.enemies){const distance=Math.hypot(e.x-p.x,e.y-p.y);if(distance<best){best=distance;target=e;}}
 if(target&&p.cool<=0){p.angle=Math.atan2(target.y-p.y,target.x-p.x);p.cool=p.interval;target.hp-=p.damage;s.shots.push({x:p.x,y:p.y,tx:target.x,ty:target.y,life:.09});if(target.hp<=0)s.kills++;}
 s.enemies=s.enemies.filter(e=>e.hp>0);
 for(const e of s.enemies){const dx=p.x-e.x,dy=p.y-e.y,d=Math.hypot(dx,dy);e.angle=Math.atan2(dy,dx);if(d>0){e.x+=dx/d*e.speed*dt;e.y+=dy/d*e.speed*dt;}if(d<14+(e.r||13)&&p.inv<=0){p.hp=Math.max(0,p.hp-20);p.inv=.8;if(!p.hp){s.dead=true;break;}}}
 s.shots=s.shots.filter(b=>(b.life-=dt)>0);
}
function choose(s,choice){if(s.dead||!s.upgrade||!['damage','rate','heal'].includes(choice))return false;if(choice==='damage')s.player.damage+=.5;if(choice==='rate')s.player.interval=Math.max(.12,s.player.interval*.85);if(choice==='heal')s.player.hp=Math.min(100,s.player.hp+40);s.upgrade=false;s.upgrades++;return true;}
const api={W,H,create,step,choose};if(typeof module!=='undefined')module.exports=api;else root.Survival=api;
})(typeof globalThis!=='undefined'?globalThis:this);