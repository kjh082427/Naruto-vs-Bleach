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
gjl1.tkzl = 1;
gjl1.tkup = -4;
gjl1.tkx = 5;
gjl1.tktm = 500;
gjl1.tkdz = "被打";
gjl1.tzpw = 50;
gjl1.tzzl = 6;
gjl1.tzup = -4;
gjl1.tzx = 4;
gjl1.tztm = 0;
gjl1.tzdz = "击飞";
gjl1.k1pw = 30;
gjl1.k1zl = 2;
gjl1.k1up = 0;
gjl1.k1x = 3;
gjl1.k1tm = 300;
gjl1.k1dz = "被打";
gjl1.k2pw = 20;
gjl1.k2zl = 1;
gjl1.k2up = 4;
gjl1.k2x = 4;
gjl1.k2tm = 400;
gjl1.k2dz = "被打";
gjl1.k3pw = 60;
gjl1.k3zl = 3;
gjl1.k3up = 7;
gjl1.k3x = 7;
gjl1.k3tm = 500;
gjl1.k3dz = "被打";
gjl1.kj1pw = 100;
gjl1.kj1zl = 13;
gjl1.kj1up = 0;
gjl1.kj1x = 12;
gjl1.kj1tm = 0;
gjl1.kj1dz = "击飞";
gjl1.kj2pw = 80;
gjl1.kj2zl = 3;
gjl1.kj2up = 0;
gjl1.kj2x = 20;
gjl1.kj2tm = 0;
gjl1.kj2dz = "击飞";
gjl1.zh1pw = 30;
gjl1.zh1zl = 1;
gjl1.zh1up = 0;
gjl1.zh1x = 4;
gjl1.zh1tm = 400;
gjl1.zh1dz = "被打";
gjl1.zh12pw = 30;
gjl1.zh12zl = 1;
gjl1.zh12up = 0;
gjl1.zh12x = 4;
gjl1.zh12tm = 400;
gjl1.zh12dz = "被打";
gjl1.kj21pw = 10;
gjl1.kj21zl = 2;
gjl1.kj21up = 0;
gjl1.kj21x = 0;
gjl1.kj21tm = 1000;
gjl1.kj21dz = "被打";
gjl1.zh2pw = 150;
gjl1.zh2zl = 3;
gjl1.zh2up = 15;
gjl1.zh2x = 7;
gjl1.zh2tm = 800;
gjl1.zh2dz = "被打";
gjl1.zh31pw = 50;
gjl1.zh31zl = 1;
gjl1.zh31up = 0;
gjl1.zh31x = 4;
gjl1.zh31tm = 700;
gjl1.zh31dz = "被打";
gjl1.zh32pw = 50;
gjl1.zh32zl = 3;
gjl1.zh32up = 5;
gjl1.zh32x = 3;
gjl1.zh32tm = 700;
gjl1.zh32dz = "被打";
gjl1.zh3pw = 60;
gjl1.zh3zl = 3;
gjl1.zh3up = 1;
gjl1.zh3x = 4;
gjl1.zh3tm = 400;
gjl1.zh3dz = "被打";
gjl1.bs2pw = 30;
gjl1.bs2zl = 4;
gjl1.bs2up = 0;
gjl1.bs2x = 2;
gjl1.bs2tm = 500;
gjl1.bs2dz = "被打";
gjl1.bspw = 230;
gjl1.bszl = 5;
gjl1.bsup = 0;
gjl1.bsx = 30;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.bs3pw = 30;
gjl1.bs3zl = 14;
gjl1.bs3up = 0;
gjl1.bs3x = 2;
gjl1.bs3tm = 500;
gjl1.bs3dz = "被打";
gjl1.sbspw = 50;
gjl1.sbszl = 1;
gjl1.sbsup = 1;
gjl1.sbsx = 1;
gjl1.sbstm = 400;
gjl1.sbsdz = "被打";
gjl1.cbs1pw = 10;
gjl1.cbs1zl = 4;
gjl1.cbs1up = 0;
gjl1.cbs1x = 0;
gjl1.cbs1tm = 2000;
gjl1.cbs1dz = "被打";
gjl1.cbs2pw = 30;
gjl1.cbs2zl = 4;
gjl1.cbs2up = 0;
gjl1.cbs2x = 1;
gjl1.cbs2tm = 1000;
gjl1.cbs2dz = "被打";
gjl1.cbspw = 330;
gjl1.cbszl = 5;
gjl1.cbsup = 20;
gjl1.cbsx = 40;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
