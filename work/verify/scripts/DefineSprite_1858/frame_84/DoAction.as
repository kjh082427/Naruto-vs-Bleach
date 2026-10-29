if(_root.game.p1.mc.hp == _root.game.p2.mc.hp)
{
   gotoAndStop("drawgame");
   play();
}
else
{
   gotoAndStop("winner");
   play();
}
