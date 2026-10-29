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
gjl1.tkup = -10;
gjl1.tkx = 4;
gjl1.tktm = 700;
gjl1.tkdz = "被打";
gjl1.tk1pw = 30;
gjl1.tk1zl = 2;
gjl1.tk1up = -3;
gjl1.tk1x = -1;
gjl1.tk1tm = 300;
gjl1.tk1dz = "被打";
gjl1.tzpw = 150;
gjl1.tzzl = 3;
gjl1.tzup = 5;
gjl1.tzx = 8;
gjl1.tztm = 400;
gjl1.tzdz = "击飞";
gjl1.k1pw = 20;
gjl1.k1zl = 2;
gjl1.k1up = 0;
gjl1.k1x = 3;
gjl1.k1tm = 300;
gjl1.k1dz = "被打";
gjl1.k2pw = 30;
gjl1.k2zl = 2;
gjl1.k2up = 0;
gjl1.k2x = 1;
gjl1.k2tm = 400;
gjl1.k2dz = "被打";
gjl1.k3pw = 50;
gjl1.k3zl = 3;
gjl1.k3up = 0;
gjl1.k3x = 4;
gjl1.k3tm = 600;
gjl1.k3dz = "被打";
gjl1.k4pw = 50;
gjl1.k4zl = 5;
gjl1.k4up = 7;
gjl1.k4x = 3;
gjl1.k4tm = 500;
gjl1.k4dz = "被打";
gjl1.kj1pw = 10;
gjl1.kj1zl = 2;
gjl1.kj1up = 0;
gjl1.kj1x = 13;
gjl1.kj1tm = 400;
gjl1.kj1dz = "被打";
gjl1.kj12pw = 100;
gjl1.kj12zl = 3;
gjl1.kj12up = 10;
gjl1.kj12x = 5;
gjl1.kj12tm = 500;
gjl1.kj12dz = "被打";
gjl1.kj22pw = 10;
gjl1.kj22zl = 1;
gjl1.kj22up = 0;
gjl1.kj22x = 5;
gjl1.kj22tm = 400;
gjl1.kj22dz = "被打";
gjl1.kj2pw = 100;
gjl1.kj2zl = 6;
gjl1.kj2up = 0;
gjl1.kj2x = 3;
gjl1.kj2tm = 500;
gjl1.kj2dz = "被打";
gjl1.kj21pw = 80;
gjl1.kj21zl = 6;
gjl1.kj21up = 8;
gjl1.kj21x = 5;
gjl1.kj21tm = 500;
gjl1.kj21dz = "被打";
gjl1.zh1pw = 150;
gjl1.zh1zl = 7;
gjl1.zh1up = 0;
gjl1.zh1x = 10;
gjl1.zh1tm = 0;
gjl1.zh1dz = "击飞";
gjl1.zh2pw = 30;
gjl1.zh2zl = 14;
gjl1.zh2up = 0;
gjl1.zh2x = 2;
gjl1.zh2tm = 500;
gjl1.zh2dz = "被打";
gjl1.zh3pw = 20;
gjl1.zh3zl = 2;
gjl1.zh3up = 3;
gjl1.zh3x = 1;
gjl1.zh3tm = 500;
gjl1.zh3dz = "被打";
gjl1.zh31pw = 80;
gjl1.zh31zl = 3;
gjl1.zh31up = 0;
gjl1.zh31x = 0;
gjl1.zh31tm = 500;
gjl1.zh31dz = "被打";
gjl1.zh32pw = 100;
gjl1.zh32zl = 3;
gjl1.zh32up = -20;
gjl1.zh32x = 0;
gjl1.zh32tm = 0;
gjl1.zh32dz = "击飞";
gjl1.bs1pw = 30;
gjl1.bs1zl = 4;
gjl1.bs1up = 0;
gjl1.bs1x = 10;
gjl1.bs1tm = 1000;
gjl1.bs1dz = "被打";
gjl1.bs2pw = 30;
gjl1.bs2zl = 4;
gjl1.bs2up = 0;
gjl1.bs2x = 10;
gjl1.bs2tm = 0;
gjl1.bs2dz = "击飞";
gjl1.bspw = 100;
gjl1.bszl = 7;
gjl1.bsup = 0;
gjl1.bsx = 10;
gjl1.bstm = 1000;
gjl1.bsdz = "被打";
gjl1.sbspw = 30;
gjl1.sbszl = 4;
gjl1.sbsup = 0;
gjl1.sbsx = 1;
gjl1.sbstm = 200;
gjl1.sbsdz = "被打";
gjl1.sbs2pw = 80;
gjl1.sbs2zl = 5;
gjl1.sbs2up = 2;
gjl1.sbs2x = 13;
gjl1.sbs2tm = 0;
gjl1.sbs2dz = "击飞";
gjl1.cbs1pw = 100;
gjl1.cbs1zl = 17;
gjl1.cbs1up = 10;
gjl1.cbs1x = 20;
gjl1.cbs1tm = 0;
gjl1.cbs1dz = "击飞";
gjl1.cbspw = 30;
gjl1.cbszl = 4;
gjl1.cbsup = 3;
gjl1.cbsx = 5;
gjl1.cbstm = 1000;
gjl1.cbsdz = "被打";
