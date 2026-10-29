if(_root.game["p" + pn].mc.hp > 0 && _root.game["p" + pn].mc.动作 == -1)
{
   _root.game["p" + pn]._visible = false;
}
else
{
   gotoAndStop("必杀1");
   play();
}
