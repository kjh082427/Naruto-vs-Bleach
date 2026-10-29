nextfight = function()
{
   _root.rounds += 1;
   _root.焦点 = "all";
   _root.game.p1.mc.gotoAndPlay("站立");
   _root.game.p2.mc.gotoAndPlay("站立");
   _root.chushi();
   _root.game.p1.mc.fall = false;
   _root.game.p1.mc.touch = true;
   _root.game.p2.mc.fall = false;
   _root.game.p2.mc.touch = true;
   _root.game.p1.mc.sw = false;
   _root.game.p2.mc.sw = false;
   _root.game.p1.mc.gotoAndPlay("站立");
   _root.game.p2.mc.gotoAndPlay("站立");
   _root.qjxg.gotoAndPlay("开");
   _root.ready.play();
};
_root.gametime = _root.maxtime;
if(_root.p1ws == 3)
{
   if(_root.modo == 1)
   {
      _root.clearint();
      _root.gotoAndStop("YOUWIN");
   }
   if(_root.modo == 2 or _root.modo == 3)
   {
      _root.clearint();
      _root.gotoAndStop("选人画面");
   }
}
else if(_root.p2ws == 3)
{
   if(_root.modo == 1)
   {
      _root.clearint();
      _root.gotoAndStop("继续");
   }
   if(_root.modo == 2 or _root.modo == 3)
   {
      _root.clearint();
      _root.gotoAndStop("选人画面");
   }
}
else
{
   _root.nxtfht = setInterval(nextfight,1000);
}
