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
gjl1.tkpw = 50;
gjl1.tkzl = 6;
gjl1.tkup = -6;
gjl1.tkx = 6;
gjl1.tktm = 500;
gjl1.tkdz = "被打";
gjl1.tzpw = 80;
gjl1.tzzl = 5;
gjl1.tzup = 0;
gjl1.tzx = 10;
gjl1.tztm = 0;
gjl1.tzdz = "击飞";
gjl1.k1pw = 30;
gjl1.k1zl = 1;
gjl1.k1up = 0;
gjl1.k1x = 3;
gjl1.k1tm = 200;
gjl1.k1dz = "被打";
gjl1.k2pw = 30;
gjl1.k2zl = 1;
gjl1.k2up = 0;
gjl1.k2x = 5;
gjl1.k2tm = 300;
gjl1.k2dz = "被打";
gjl1.k3pw = 50;
gjl1.k3zl = 6;
gjl1.k3up = 0;
gjl1.k3x = 10;
gjl1.k3tm = 600;
gjl1.k3dz = "被打";
gjl1.k4pw = 50;
gjl1.k4zl = 6;
gjl1.k4up = 0;
gjl1.k4x = 3;
gjl1.k4tm = 400;
gjl1.k4dz = "被打";
gjl1.k5pw = 20;
gjl1.k5zl = 1;
gjl1.k5up = 5;
gjl1.k5x = 3;
gjl1.k5tm = 600;
gjl1.k5dz = "被打";
gjl1.kj2pw = 120;
gjl1.kj2zl = 15;
gjl1.kj2up = 10;
gjl1.kj2x = 10;
gjl1.kj2tm = 0;
gjl1.kj2dz = "击飞";
gjl1.kj21pw = 40;
gjl1.kj21zl = 1;
gjl1.kj21up = 0;
gjl1.kj21x = 1;
gjl1.kj21tm = 100;
gjl1.kj21dz = "被打";
gjl1.kj22pw = 50;
gjl1.kj22zl = 6;
gjl1.kj22up = 0;
gjl1.kj22x = 7;
gjl1.kj22tm = 0;
gjl1.kj22dz = "击飞";
gjl1.kj1pw = 100;
gjl1.kj1zl = 6;
gjl1.kj1up = 0;
gjl1.kj1x = 3;
gjl1.kj1tm = 500;
gjl1.kj1dz = "被打";
gjl1.kj12pw = 110;
gjl1.kj12zl = 6;
gjl1.kj12up = 0;
gjl1.kj12x = 7;
gjl1.kj12tm = 0;
gjl1.kj12dz = "击飞";
gjl1.zh1pw = 100;
gjl1.zh1zl = 9;
gjl1.zh1up = 0;
gjl1.zh1x = 15;
gjl1.zh1tm = 0;
gjl1.zh1dz = "击飞";
gjl1.zh2pw = 110;
gjl1.zh2zl = 15;
gjl1.zh2up = 5;
gjl1.zh2x = 30;
gjl1.zh2tm = 0;
gjl1.zh2dz = "击飞";
gjl1.zh3pw = 50;
gjl1.zh3zl = 5;
gjl1.zh3up = 6;
gjl1.zh3x = 5;
gjl1.zh3tm = 700;
gjl1.zh3dz = "被打";
gjl1.zh31pw = 100;
gjl1.zh31zl = 5;
gjl1.zh31up = 3;
gjl1.zh31x = 20;
gjl1.zh31tm = 0;
gjl1.zh31dz = "击飞";
gjl1.bs1pw = 20;
gjl1.bs1zl = 1;
gjl1.bs1up = 1;
gjl1.bs1x = 0;
gjl1.bs1tm = 500;
gjl1.bs1dz = "被打";
gjl1.bspw = 80;
gjl1.bszl = 5;
gjl1.bsup = 0;
gjl1.bsx = 10;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.sbspw = 150;
gjl1.sbszl = 5;
gjl1.sbsup = 15;
gjl1.sbsx = 0;
gjl1.sbstm = 0;
gjl1.sbsdz = "击飞";
gjl1.sbs1pw = 30;
gjl1.sbs1zl = 1;
gjl1.sbs1up = 0;
gjl1.sbs1x = 3;
gjl1.sbs1tm = 500;
gjl1.sbs1dz = "被打";
gjl1.sbs2pw = 30;
gjl1.sbs2zl = 1;
gjl1.sbs2up = 4;
gjl1.sbs2x = 4;
gjl1.sbs2tm = 500;
gjl1.sbs2dz = "被打";
gjl1.sbs3pw = 30;
gjl1.sbs3zl = 1;
gjl1.sbs3up = -4;
gjl1.sbs3x = 4;
gjl1.sbs3tm = 500;
gjl1.sbs3dz = "被打";
gjl1.sbs4pw = 50;
gjl1.sbs4zl = 6;
gjl1.sbs4up = 0;
gjl1.sbs4x = 2;
gjl1.sbs4tm = 1000;
gjl1.sbs4dz = "被打";
gjl1.kbspw = 200;
gjl1.kbszl = 5;
gjl1.kbsup = -5;
gjl1.kbsx = 15;
gjl1.kbstm = 0;
gjl1.kbsdz = "击飞";
gjl1.cbspw = 20;
gjl1.cbszl = 4;
gjl1.cbsup = 1;
gjl1.cbsx = 1;
gjl1.cbstm = 500;
gjl1.cbsdz = "被打";
gjl1.cbs2pw = 40;
gjl1.cbs2zl = 15;
gjl1.cbs2up = 10;
gjl1.cbs2x = 2;
gjl1.cbs2tm = 0;
gjl1.cbs2dz = "击飞";
