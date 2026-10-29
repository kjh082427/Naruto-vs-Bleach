if(_root.game["p" + pn].mc.hp <= 0)
{
   return undefined;
}
if(_root.game["p" + pn].mc.动作 == -1)
{
   gotoAndStop("超必杀1");
   play();
   return undefined;
}
if(cbs0atm.hitTest(_root.game["p" + pn].mc.bdmn))
{
   gotoAndStop("超必杀1");
   play();
}
