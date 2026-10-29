function initCtrl(ai)
{
   useAI = ai;
   mc.initCtrl();
}
function updateGJL()
{
   trace("updateGJL");
   _curGJL = _this["gjl" + _this._currentframe];
   var _loc2_ = _this._name != "p1" ? _root.game.p1 : _root.game.p2;
   var _loc3_ = _this._name != "p1" ? _root.game.p1fz : _root.game.p2fz;
   mc.pw = _loc2_["gjl" + _loc2_._currentframe];
   mc.fzpw = _loc3_.gjl;
}
function setColor(cls)
{
   mc.colors = cls;
}
function showdow(rgb)
{
   if(++_si > 1)
   {
      _si = 0;
      return undefined;
   }
   var _loc3_;
   if(rgb != null)
   {
      _loc3_ = new flash.geom.ColorTransform();
      if(!isNaN(rgb.R))
      {
         _loc3_.redOffset = rgb.R;
      }
      if(!isNaN(rgb.G))
      {
         _loc3_.greenOffset = rgb.G;
      }
      if(!isNaN(rgb.B))
      {
         _loc3_.blueOffset = rgb.B;
      }
   }
   _root.shadowEffect(_this,{alphaStart:100,alphaLose:10,colorTransform:_loc3_});
}
function moveX(spd)
{
   _X = _X + spd * scale_X;
}
function moveY(spd)
{
   _Y = _Y + spd;
}
var 中转 = new Array();
var 万解 = false;
var useAI;
var _this = this;
var _curGJL;
var scale_X = 1;
var hitWall = false;
var isNaruto;
var heavy = 2;
var hitTarget = false;
var vecx = 0;
if(_root.zhanting == undefined)
{
   this.unloadMovie();
}
var _si = 0;
stop();
var gjl1 = [];
gjl1.tkpw = 40;
gjl1.tkzl = 1;
gjl1.tkup = 0;
gjl1.tkx = 5;
gjl1.tktm = 400;
gjl1.tkdz = "被打";
gjl1.tzpw = 80;
gjl1.tzzl = 8;
gjl1.tzup = -5;
gjl1.tzx = 5;
gjl1.tztm = 0;
gjl1.tzdz = "击飞";
gjl1.k1pw = 30;
gjl1.k1zl = 1;
gjl1.k1up = 0;
gjl1.k1x = 2;
gjl1.k1tm = 300;
gjl1.k1dz = "被打";
gjl1.k2pw = 40;
gjl1.k2zl = 1;
gjl1.k2up = 0;
gjl1.k2x = 3;
gjl1.k2tm = 400;
gjl1.k2dz = "被打";
gjl1.k3pw = 70;
gjl1.k3zl = 6;
gjl1.k3up = 5;
gjl1.k3x = 5;
gjl1.k3tm = 400;
gjl1.k3dz = "被打";
gjl1.kj1pw = 100;
gjl1.kj1zl = 5;
gjl1.kj1up = 4;
gjl1.kj1x = 8;
gjl1.kj1tm = 0;
gjl1.kj1dz = "击飞";
gjl1.kj21pw = 50;
gjl1.kj21zl = 1;
gjl1.kj21up = 0;
gjl1.kj21x = 3;
gjl1.kj21tm = 300;
gjl1.kj21dz = "被打";
gjl1.kj2pw = 70;
gjl1.kj2zl = 8;
gjl1.kj2up = 0;
gjl1.kj2x = 5;
gjl1.kj2tm = 0;
gjl1.kj2dz = "击飞";
gjl1.zh1pw = 25;
gjl1.zh1zl = 4;
gjl1.zh1up = 0;
gjl1.zh1x = 22;
gjl1.zh1tm = 100;
gjl1.zh1dz = "被打";
gjl1.zh2pw = 50;
gjl1.zh2zl = 18;
gjl1.zh2up = 0;
gjl1.zh2x = -2;
gjl1.zh2tm = 600;
gjl1.zh2dz = "被打";
gjl1.zh3pw = 40;
gjl1.zh3zl = 4;
gjl1.zh3up = 7;
gjl1.zh3x = 6;
gjl1.zh3tm = 500;
gjl1.zh3dz = "被打";
gjl1.bspw = 300;
gjl1.bszl = 8;
gjl1.bsup = 0;
gjl1.bsx = 20;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.sbspw = 220;
gjl1.sbszl = 8;
gjl1.sbsup = 8;
gjl1.sbsx = 3;
gjl1.sbstm = 0;
gjl1.sbsdz = "击飞";
gjl1.cbs1pw = 15;
gjl1.cbs1zl = 4;
gjl1.cbs1up = 0;
gjl1.cbs1x = 0;
gjl1.cbs1tm = 100;
gjl1.cbs1dz = "被打";
gjl1.cbspw = 150;
gjl1.cbszl = 15;
gjl1.cbsup = 0;
gjl1.cbsx = 20;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
var gjl2 = [];
gjl2.tkpw = 30;
gjl2.tkzl = 1;
gjl2.tkup = -3;
gjl2.tkx = 0;
gjl2.tktm = 400;
gjl2.tkdz = "被打";
gjl2.tzpw = 80;
gjl2.tzzl = 8;
gjl2.tzup = -10;
gjl2.tzx = 10;
gjl2.tztm = 0;
gjl2.tzdz = "击飞";
gjl2.k1pw = 30;
gjl2.k1zl = 1;
gjl2.k1up = 0;
gjl2.k1x = 3;
gjl2.k1tm = 400;
gjl2.k1dz = "被打";
gjl2.k2pw = 40;
gjl2.k2zl = 1;
gjl2.k2up = 0;
gjl2.k2x = 4;
gjl2.k2tm = 400;
gjl2.k2dz = "被打";
gjl2.k3pw = 50;
gjl2.k3zl = 1;
gjl2.k3up = 7;
gjl2.k3x = 7;
gjl2.k3tm = 500;
gjl2.k3dz = "被打";
gjl2.kj1pw = 80;
gjl2.kj1zl = 16;
gjl2.kj1up = 0;
gjl2.kj1x = 10;
gjl2.kj1tm = 0;
gjl2.kj1dz = "击飞";
gjl2.kj21pw = 50;
gjl2.kj21zl = 1;
gjl2.kj21up = 7;
gjl2.kj21x = 5;
gjl2.kj21tm = 600;
gjl2.kj21dz = "被打";
gjl2.kj2pw = 100;
gjl2.kj2zl = 5;
gjl2.kj2up = -5;
gjl2.kj2x = 10;
gjl2.kj2tm = 0;
gjl2.kj2dz = "击飞";
gjl2.zh1pw = 30;
gjl2.zh1zl = 4;
gjl2.zh1up = 0;
gjl2.zh1x = 10;
gjl2.zh1tm = 400;
gjl2.zh1dz = "被打";
gjl2.zh2pw = 100;
gjl2.zh2zl = 8;
gjl2.zh2up = 0;
gjl2.zh2x = 10;
gjl2.zh2tm = 0;
gjl2.zh2dz = "击飞";
gjl2.zh3pw = 120;
gjl2.zh3zl = 8;
gjl2.zh3up = 7;
gjl2.zh3x = 5;
gjl2.zh3tm = 500;
gjl2.zh3dz = "击飞";
gjl2.bspw = 250;
gjl2.bszl = 18;
gjl2.bsup = 0;
gjl2.bsx = 20;
gjl2.bstm = 0;
gjl2.bsdz = "击飞";
gjl2.sbspw = 320;
gjl2.sbszl = 6;
gjl2.sbsup = 8;
gjl2.sbsx = 3;
gjl2.sbstm = 0;
gjl2.sbsdz = "击飞";
gjl2.cbs1pw = 10;
gjl2.cbs1zl = 4;
gjl2.cbs1up = -10;
gjl2.cbs1x = 0;
gjl2.cbs1tm = 0;
gjl2.cbs1dz = "被打";
gjl2.cbspw = 400;
gjl2.cbszl = 8;
gjl2.cbsup = 0;
gjl2.cbsx = 20;
gjl2.cbstm = 0;
gjl2.cbsdz = "击飞";
gjl2.cbs3pw = 10;
gjl2.cbs3zl = 4;
gjl2.cbs3up = 5;
gjl2.cbs3x = 0;
gjl2.cbs3tm = 5000;
gjl2.cbs3dz = "被打";
gjl2.cbs2pw = 0;
gjl2.cbs2tm = 5000;
