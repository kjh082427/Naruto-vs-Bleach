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
gjl1.tkpw = 30;
gjl1.tkzl = 2;
gjl1.tkup = 0;
gjl1.tkx = 2;
gjl1.tktm = 400;
gjl1.tkdz = "被打";
gjl1.tzpw = 100;
gjl1.tzzl = 3;
gjl1.tzup = -10;
gjl1.tzx = 5;
gjl1.tztm = 0;
gjl1.tzdz = "击飞";
gjl1.k1pw = 40;
gjl1.k1zl = 2;
gjl1.k1up = 0;
gjl1.k1x = 2;
gjl1.k1tm = 300;
gjl1.k1dz = "被打";
gjl1.k2pw = 40;
gjl1.k2zl = 2;
gjl1.k2up = 0;
gjl1.k2x = 6;
gjl1.k2tm = 300;
gjl1.k2dz = "被打";
gjl1.k3pw = 80;
gjl1.k3zl = 3;
gjl1.k3up = 8;
gjl1.k3x = 3;
gjl1.k3tm = 400;
gjl1.k3dz = "被打";
gjl1.kj1pw = 100;
gjl1.kj1zl = 3;
gjl1.kj1up = 0;
gjl1.kj1x = 10;
gjl1.kj1tm = 600;
gjl1.kj1dz = "被打";
gjl1.kj2pw = 20;
gjl1.kj2zl = 12;
gjl1.kj2up = 0;
gjl1.kj2x = 0;
gjl1.kj2tm = 500;
gjl1.kj2dz = "被打";
gjl1.kj21pw = 50;
gjl1.kj21zl = 0;
gjl1.kj21up = 0;
gjl1.kj21x = -15;
gjl1.kj21tm = 0;
gjl1.kj21dz = "击飞";
gjl1.zh1pw = 50;
gjl1.zh1zl = 4;
gjl1.zh1up = 0;
gjl1.zh1x = 8;
gjl1.zh1tm = 500;
gjl1.zh1dz = "被打";
gjl1.zh11pw = 50;
gjl1.zh11zl = 7;
gjl1.zh11up = 0;
gjl1.zh11x = 8;
gjl1.zh11tm = 500;
gjl1.zh11dz = "击飞";
gjl1.zh21pw = 10;
gjl1.zh21zl = 2;
gjl1.zh21up = 0;
gjl1.zh21x = 0;
gjl1.zh21tm = 300;
gjl1.zh21dz = "被打";
gjl1.zh2pw = 50;
gjl1.zh2zl = 13;
gjl1.zh2up = 0;
gjl1.zh2x = 0;
gjl1.zh2tm = 600;
gjl1.zh2dz = "被打";
gjl1.zh22pw = 120;
gjl1.zh22zl = 17;
gjl1.zh22up = 0;
gjl1.zh22x = 20;
gjl1.zh22tm = 0;
gjl1.zh22dz = "击飞";
gjl1.zh3pw = 100;
gjl1.zh3zl = 3;
gjl1.zh3up = 10;
gjl1.zh3x = 10;
gjl1.zh3tm = 500;
gjl1.zh3dz = "被打";
gjl1.zh32pw = 80;
gjl1.zh32zl = 0;
gjl1.zh32up = -10;
gjl1.zh32x = -15;
gjl1.zh32tm = 0;
gjl1.zh32dz = "击飞";
gjl1.bs1pw = 50;
gjl1.bs1zl = 4;
gjl1.bs1up = 0;
gjl1.bs1x = 5;
gjl1.bs1tm = 2000;
gjl1.bs1dz = "被打";
gjl1.bspw = 150;
gjl1.bszl = 5;
gjl1.bsup = 0;
gjl1.bsx = 20;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.sbs1pw = 100;
gjl1.sbs1zl = 3;
gjl1.sbs1up = 2;
gjl1.sbs1x = 2;
gjl1.sbs1tm = 2000;
gjl1.sbs1dz = "被打";
gjl1.sbspw = 200;
gjl1.sbszl = 5;
gjl1.sbsup = 2;
gjl1.sbsx = 20;
gjl1.sbstm = 0;
gjl1.sbsdz = "击飞";
gjl1.cbs1pw = 50;
gjl1.cbs1zl = 13;
gjl1.cbs1up = 0;
gjl1.cbs1x = 0;
gjl1.cbs1tm = 3000;
gjl1.cbs1dz = "被打";
gjl1.cbs2pw = 50;
gjl1.cbs2zl = 0;
gjl1.cbs2up = 0;
gjl1.cbs2x = 0;
gjl1.cbs2tm = 3000;
gjl1.cbs2dz = "被打";
gjl1.cbspw = 150;
gjl1.cbszl = 13;
gjl1.cbsup = 5;
gjl1.cbsx = 10;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
