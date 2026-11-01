p1head.namemc.gotoAndStop(_root.p1selt);
p2head.namemc.gotoAndStop(_root.p2selt);
var p1obj = _root.getFighterData(_root.p1selt);
var p2obj = _root.getFighterData(_root.p2selt);
txt_p1.text = p1obj.name;
txt_p2.text = p2obj.name;
var p1hp;
var p2hp;
var bar2Spd = _root.maxhp / 500;
onEnterFrame = function()
{
   p1hp = _root.game.p1.mc.hp / _root.maxhp * 100;
   p2hp = _root.game.p2.mc.hp / _root.maxhp * 100;
   p1xt.bar.msk._xscale = p1hp;
   p2xt.bar.msk._xscale = p2hp;
   if(p1hp <= 0 || p2hp <= 0)
   {
      return undefined;
   }
   if(p1xt.bar._xscale < 20)
   {
      p1xt.kk.gotoAndStop(2);
      _root.game.p1.mc.ql += 0.2;
   }
   if(p2xt.bar._xscale < 20)
   {
      p2xt.kk.gotoAndStop(2);
      _root.game.p2.mc.ql += 0.2;
   }
   var _loc2_ = _root.game.p2.mc.hits;
   var _loc3_ = _root.game.p1.mc.hits;
   if(_loc3_ == 0)
   {
      if(p1xt.bar2._xscale > p1hp)
      {
         p1xt.bar2._xscale -= bar2Spd;
      }
      else
      {
         p1xt.bar2._xscale = p1hp;
      }
   }
   if(_loc2_ == 0)
   {
      if(p2xt.bar2._xscale > p2hp)
      {
         p2xt.bar2._xscale -= bar2Spd;
      }
      else
      {
         p2xt.bar2._xscale = p2hp;
      }
   }
};
_root.xuntiaoInitlize = function()
{
   p1xt.bar.msk._xscale = 100;
   p1xt.bar2._xscale = 100;
   p2xt.bar.msk._xscale = 100;
   p2xt.bar2._xscale = 100;
   p1xt.kk.gotoAndStop(1);
   p2xt.kk.gotoAndStop(1);
};
_root.updateWins = function()
{
   trace("updateWins");
   win1.gotoAndStop(_root.p1ws);
   win2.gotoAndStop(_root.p2ws);
};
