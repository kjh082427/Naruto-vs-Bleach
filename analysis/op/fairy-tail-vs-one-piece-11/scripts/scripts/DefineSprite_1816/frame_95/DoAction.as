if(_root.game.p2.mc.sw == true)
{
   _root.p1ws += 1;
   _root.updateWins();
   _root.焦点 = "p1";
}
if(_root.game.p1.mc.sw == true)
{
   _root.p2ws += 1;
   _root.updateWins();
   _root.焦点 = "p2";
}
