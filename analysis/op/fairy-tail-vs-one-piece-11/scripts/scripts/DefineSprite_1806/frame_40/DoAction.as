if(_root.game.p1.mc.hp > _root.game.p2.mc.hp)
{
   _root.game.p2.mc.gotoAndPlay("失败");
}
if(_root.game.p1.mc.hp < _root.game.p2.mc.hp)
{
   _root.game.p1.mc.gotoAndPlay("失败");
}
if(_root.game.p1.mc.hp == _root.game.p2.mc.hp)
{
   _root.game.p1.mc.gotoAndPlay("失败");
   _root.game.p2.mc.gotoAndPlay("失败");
}
