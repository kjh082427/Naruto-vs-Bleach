if(_root.game.p1.mc.hp > _root.game.p2.mc.hp)
{
   _root.p1ws += 1;
   _root.p1win.gotoAndStop(_root.p1ws);
   _root.p1win.bzxg.play();
   _root.焦点 = "p1";
}
else
{
   _root.p2ws += 1;
   _root.p2win.gotoAndStop(_root.p2ws);
   _root.p2win.bzxg.play();
   _root.焦点 = "p2";
}
