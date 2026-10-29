if(_root.game.p1.mc.hp > _root.game.p2.mc.hp)
{
   _root.p1ws += 1;
   _root.updateWins();
   _root.焦点 = "p1";
   winmc._x = 0;
}
else
{
   _root.p2ws += 1;
   _root.updateWins();
   _root.焦点 = "p2";
   winmc._x = 120;
}
