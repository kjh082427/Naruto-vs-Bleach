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
gjl1.tkup = -6;
gjl1.tkx = 2;
gjl1.tktm = 300;
gjl1.tkdz = "被打";
gjl1.tzpw = 80;
gjl1.tzzl = 5;
gjl1.tzup = -5;
gjl1.tzx = 3;
gjl1.tztm = 300;
gjl1.tzdz = "击飞";
gjl1.k1pw = 40;
gjl1.k1zl = 1;
gjl1.k1up = 0;
gjl1.k1x = 3;
gjl1.k1tm = 300;
gjl1.k1dz = "被打";
gjl1.k2pw = 50;
gjl1.k2zl = 1;
gjl1.k2up = 0;
gjl1.k2x = 2;
gjl1.k2tm = 400;
gjl1.k2dz = "被打";
gjl1.k3pw = 70;
gjl1.k3zl = 6;
gjl1.k3up = 7;
gjl1.k3x = 7;
gjl1.k3tm = 600;
gjl1.k3dz = "被打";
gjl1.kj1pw = 80;
gjl1.kj1zl = 13;
gjl1.kj1up = 0;
gjl1.kj1x = 8;
gjl1.kj1tm = 0;
gjl1.kj1dz = "击飞";
gjl1.kj21pw = 20;
gjl1.kj21zl = 1;
gjl1.kj21up = 0;
gjl1.kj21x = 1;
gjl1.kj21tm = 100;
gjl1.kj21dz = "被打";
gjl1.kj2pw = 60;
gjl1.kj2zl = 4;
gjl1.kj2up = 12;
gjl1.kj2x = 1;
gjl1.kj2tm = 500;
gjl1.kj2dz = "被打";
gjl1.zh1pw = 80;
gjl1.zh1zl = 5;
gjl1.zh1up = 0;
gjl1.zh1x = 3;
gjl1.zh1tm = 300;
gjl1.zh1dz = "击飞";
gjl1.zh2pw = 80;
gjl1.zh2zl = 6;
gjl1.zh2up = 3;
gjl1.zh2x = 8;
gjl1.zh2tm = 700;
gjl1.zh2dz = "被打";
gjl1.zh3pw = 80;
gjl1.zh3zl = 5;
gjl1.zh3up = 6;
gjl1.zh3x = 3;
gjl1.zh3tm = 300;
gjl1.zh3dz = "击飞";
gjl1.bspw = 300;
gjl1.bszl = 5;
gjl1.bsup = 0;
gjl1.bsx = 20;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.sbspw = 250;
gjl1.sbszl = 5;
gjl1.sbsup = 8;
gjl1.sbsx = 3;
gjl1.sbstm = 0;
gjl1.sbsdz = "击飞";
gjl1.cbspw = 450;
gjl1.cbszl = 5;
gjl1.cbsup = 0;
gjl1.cbsx = 40;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
var gjl2 = [];
gjl2.tkpw = 40;
gjl2.tkzl = 1;
gjl2.tkup = -6;
gjl2.tkx = 2;
gjl2.tktm = 300;
gjl2.tkdz = "被打";
gjl2.tzpw = 110;
gjl2.tzzl = 6;
gjl2.tzup = 0;
gjl2.tzx = 10;
gjl2.tztm = 0;
gjl2.tzdz = "击飞";
gjl2.k1pw = 30;
gjl2.k1zl = 1;
gjl2.k1up = 0;
gjl2.k1x = 2;
gjl2.k1tm = 300;
gjl2.k1dz = "被打";
gjl2.k2pw = 30;
gjl2.k2zl = 1;
gjl2.k2up = 0;
gjl2.k2x = 2;
gjl2.k2tm = 400;
gjl2.k2dz = "被打";
gjl2.k3pw = 40;
gjl2.k3zl = 1;
gjl2.k3up = 7;
gjl2.k3x = 7;
gjl2.k3tm = 400;
gjl2.k3dz = "被打";
gjl2.kj1pw = 80;
gjl2.kj1zl = 15;
gjl2.kj1up = 0;
gjl2.kj1x = -2;
gjl2.kj1tm = 500;
gjl2.kj1dz = "被打";
gjl2.kj21pw = 20;
gjl2.kj21zl = 4;
gjl2.kj21up = 20;
gjl2.kj21x = 1;
gjl2.kj21tm = 100;
gjl2.kj21dz = "被打";
gjl2.kj2pw = 70;
gjl2.kj2zl = 6;
gjl2.kj2up = -10;
gjl2.kj2x = 1;
gjl2.kj2tm = 550;
gjl2.kj2dz = "被打";
gjl2.zh1pw = 50;
gjl2.zh1zl = 6;
gjl2.zh1up = 0;
gjl2.zh1x = 2;
gjl2.zh1tm = 500;
gjl2.zh1dz = "被打";
gjl2.zh2pw = 80;
gjl2.zh2zl = 6;
gjl2.zh2up = 0;
gjl2.zh2x = 12;
gjl2.zh2tm = 0;
gjl2.zh2dz = "击飞";
gjl2.zh3pw = 80;
gjl2.zh3zl = 6;
gjl2.zh3up = 4;
gjl2.zh3x = 4;
gjl2.zh3tm = 0;
gjl2.zh3dz = "击飞";
gjl2.bspw = 300;
gjl2.bszl = 5;
gjl2.bsup = 0;
gjl2.bsx = 25;
gjl2.bstm = 0;
gjl2.bsdz = "击飞";
gjl2.sbspw = 20;
gjl2.sbszl = 1;
gjl2.sbsup = 1;
gjl2.sbsx = 0;
gjl2.sbstm = 300;
gjl2.sbsdz = "被打";
gjl2.sbs2pw = 20;
gjl2.sbs2zl = 1;
gjl2.sbs2up = 5;
gjl2.sbs2x = 0;
gjl2.sbs2tm = 0;
gjl2.sbs2dz = "击飞";
gjl2.cbspw = 600;
gjl2.cbszl = 5;
gjl2.cbsup = 0;
gjl2.cbsx = 30;
gjl2.cbstm = 0;
gjl2.cbsdz = "击飞";
var gjl3 = [];
gjl3.tkpw = 50;
gjl3.tkzl = 1;
gjl3.tkup = -5;
gjl3.tkx = 5;
gjl3.tktm = 500;
gjl3.tkdz = "被打";
gjl3.tzpw = 20;
gjl3.tzzl = 1;
gjl3.tzup = -5;
gjl3.tzx = 5;
gjl3.tztm = 500;
gjl3.tzdz = "被打";
gjl3.tz1pw = 70;
gjl3.tz1zl = 5;
gjl3.tz1up = 0;
gjl3.tz1x = 10;
gjl3.tz1tm = 0;
gjl3.tz1dz = "击飞";
gjl3.k1pw = 30;
gjl3.k1zl = 1;
gjl3.k1up = 0;
gjl3.k1x = 5;
gjl3.k1tm = 300;
gjl3.k1dz = "被打";
gjl3.k2pw = 30;
gjl3.k2zl = 1;
gjl3.k2up = 0;
gjl3.k2x = 3;
gjl3.k2tm = 300;
gjl3.k2dz = "被打";
gjl3.k3pw = 30;
gjl3.k3zl = 1;
gjl3.k3up = 0;
gjl3.k3x = 3;
gjl3.k3tm = 300;
gjl3.k3dz = "被打";
gjl3.k4pw = 80;
gjl3.k4zl = 6;
gjl3.k4up = 0;
gjl3.k4x = 6;
gjl3.k4tm = 800;
gjl3.k4dz = "被打";
gjl3.k5pw = 60;
gjl3.k5zl = 1;
gjl3.k5up = 7;
gjl3.k5x = 7;
gjl3.k5tm = 600;
gjl3.k5dz = "被打";
gjl3.kj1pw = 90;
gjl3.kj1zl = 15;
gjl3.kj1up = 5;
gjl3.kj1x = 10;
gjl3.kj1tm = 0;
gjl3.kj1dz = "击飞";
gjl3.kj21pw = 110;
gjl3.kj21zl = 5;
gjl3.kj21up = -8;
gjl3.kj21x = 12;
gjl3.kj21tm = 0;
gjl3.kj21dz = "击飞";
gjl3.kj2pw = 50;
gjl3.kj2zl = 6;
gjl3.kj2up = 8;
gjl3.kj2x = 15;
gjl3.kj2tm = 700;
gjl3.kj2dz = "被打";
gjl3.zh1pw = 50;
gjl3.zh1zl = 1;
gjl3.zh1up = 0;
gjl3.zh1x = 2;
gjl3.zh1tm = 500;
gjl3.zh1dz = "被打";
gjl3.zh12pw = 50;
gjl3.zh12zl = 6;
gjl3.zh12up = 0;
gjl3.zh12x = 4;
gjl3.zh12tm = 600;
gjl3.zh12dz = "被打";
gjl3.zh2pw = 100;
gjl3.zh2zl = 6;
gjl3.zh2up = 10;
gjl3.zh2x = 5;
gjl3.zh2tm = 800;
gjl3.zh2dz = "被打";
gjl3.zh3pw = 100;
gjl3.zh3zl = 5;
gjl3.zh3up = 8;
gjl3.zh3x = 12;
gjl3.zh3tm = 0;
gjl3.zh3dz = "击飞";
gjl3.bspw = 300;
gjl3.bszl = 5;
gjl3.bsup = 0;
gjl3.bsx = 25;
gjl3.bstm = 0;
gjl3.bsdz = "击飞";
gjl3.sbspw = 300;
gjl3.sbszl = 15;
gjl3.sbsup = 10;
gjl3.sbsx = 20;
gjl3.sbstm = 0;
gjl3.sbsdz = "击飞";
gjl3.cbspw = 500;
gjl3.cbszl = 5;
gjl3.cbsup = 20;
gjl3.cbsx = 30;
gjl3.cbstm = 0;
gjl3.cbsdz = "击飞";
gjl3.cbs1pw = 100;
gjl3.cbs1zl = 16;
gjl3.cbs1up = 7;
gjl3.cbs1x = 7;
gjl3.cbs1tm = 1000;
gjl3.cbs1dz = "被打";
