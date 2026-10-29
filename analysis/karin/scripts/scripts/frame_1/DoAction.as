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
gjl1.tkpw = 20;
gjl1.tkzl = 2;
gjl1.tkup = -4;
gjl1.tkx = 4;
gjl1.tktm = 400;
gjl1.tkdz = "被打";
gjl1.tzpw = 120;
gjl1.tzzl = 6;
gjl1.tzup = -5;
gjl1.tzx = 5;
gjl1.tztm = 0;
gjl1.tzdz = "击飞";
gjl1.tz2pw = 80;
gjl1.tz2zl = 6;
gjl1.tz2up = 5;
gjl1.tz2x = 10;
gjl1.tz2tm = 0;
gjl1.tz2dz = "击飞";
gjl1.tz3pw = 80;
gjl1.tz3zl = 6;
gjl1.tz3up = -5;
gjl1.tz3x = -10;
gjl1.tz3tm = 0;
gjl1.tz3dz = "击飞";
gjl1.tz4pw = 80;
gjl1.tz4zl = 6;
gjl1.tz4up = -5;
gjl1.tz4x = 10;
gjl1.tz4tm = 0;
gjl1.tz4dz = "击飞";
gjl1.k1pw = 20;
gjl1.k1zl = 2;
gjl1.k1up = 0;
gjl1.k1x = 4;
gjl1.k1tm = 300;
gjl1.k1dz = "被打";
gjl1.k2pw = 30;
gjl1.k2zl = 2;
gjl1.k2up = 0;
gjl1.k2x = 4;
gjl1.k2tm = 500;
gjl1.k2dz = "被打";
gjl1.k3pw = 70;
gjl1.k3zl = 3;
gjl1.k3up = 0;
gjl1.k3x = 5;
gjl1.k3tm = 600;
gjl1.k3dz = "被打";
gjl1.k4pw = 70;
gjl1.k4zl = 3;
gjl1.k4up = 0;
gjl1.k4x = 10;
gjl1.k4tm = 600;
gjl1.k4dz = "被打";
gjl1.kj1pw = 20;
gjl1.kj1zl = 4;
gjl1.kj1up = 0;
gjl1.kj1x = 3;
gjl1.kj1tm = 500;
gjl1.kj1dz = "被打";
gjl1.kj21pw = 30;
gjl1.kj21zl = 1;
gjl1.kj21up = 0;
gjl1.kj21x = 4;
gjl1.kj21tm = 600;
gjl1.kj21dz = "被打";
gjl1.kj22pw = 30;
gjl1.kj22zl = 2;
gjl1.kj22up = 0;
gjl1.kj22x = 4;
gjl1.kj22tm = 600;
gjl1.kj22dz = "被打";
gjl1.kj2pw = 100;
gjl1.kj2zl = 6;
gjl1.kj2up = 8;
gjl1.kj2x = 6;
gjl1.kj2tm = 600;
gjl1.kj2dz = "被打";
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
gjl1.zh2pw = 80;
gjl1.zh2zl = 15;
gjl1.zh2up = 10;
gjl1.zh2x = 6;
gjl1.zh2tm = 800;
gjl1.zh2dz = "被打";
gjl1.zh3pw = 160;
gjl1.zh3zl = 6;
gjl1.zh3up = 5;
gjl1.zh3x = 5;
gjl1.zh3tm = 0;
gjl1.zh3dz = "击飞";
gjl1.bspw = 230;
gjl1.bszl = 5;
gjl1.bsup = 3;
gjl1.bsx = 5;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.sbspw = 100;
gjl1.sbszl = 5;
gjl1.sbsup = 5;
gjl1.sbsx = 15;
gjl1.sbstm = 0;
gjl1.sbsdz = "击飞";
gjl1.cbs1pw = 50;
gjl1.cbs1zl = 5;
gjl1.cbs1up = 0;
gjl1.cbs1x = 0;
gjl1.cbs1tm = 2000;
gjl1.cbs1dz = "被打";
gjl1.cbs2pw = 50;
gjl1.cbs2zl = 6;
gjl1.cbs2up = 0;
gjl1.cbs2x = 0;
gjl1.cbs2tm = 2000;
gjl1.cbs2dz = "被打";
gjl1.cbspw = 350;
gjl1.cbszl = 17;
gjl1.cbsup = 10;
gjl1.cbsx = 20;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
