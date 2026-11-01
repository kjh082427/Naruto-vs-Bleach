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
   _root.shadowEffect(_this._name,{alphaStart:100,alphaLose:10,colorTransform:_loc3_});
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
var vecx = 0;
if(_root.zhanting == undefined)
{
   this.unloadMovie();
}
if(_root.HASH != "5dplay_fvo")
{
   this.unloadMovie();
}
var _si = 0;
stop();
var heavy = 1;
var gjl1 = [];
gjl1.tkpw = 30;
gjl1.tkzl = 2;
gjl1.tkup = 0;
gjl1.tkx = -5;
gjl1.tktm = 700;
gjl1.tkdz = "被打";
gjl1.tz1pw = 30;
gjl1.tz1zl = 2;
gjl1.tz1up = 0;
gjl1.tz1x = 0;
gjl1.tz1tm = 1000;
gjl1.tz1dz = "被打";
gjl1.tzpw = 100;
gjl1.tzzl = 3;
gjl1.tzup = -10;
gjl1.tzx = 0;
gjl1.tztm = 0;
gjl1.tzdz = "击飞";
gjl1.k1pw = 20;
gjl1.k1zl = 2;
gjl1.k1up = 0;
gjl1.k1x = 2;
gjl1.k1tm = 400;
gjl1.k1dz = "被打";
gjl1.k2pw = 20;
gjl1.k2zl = 2;
gjl1.k2up = 0;
gjl1.k2x = 4;
gjl1.k2tm = 400;
gjl1.k2dz = "被打";
gjl1.k3pw = 60;
gjl1.k3zl = 3;
gjl1.k3up = 8;
gjl1.k3x = 0;
gjl1.k3tm = 500;
gjl1.k3dz = "被打";
gjl1.kj1pw = 0;
gjl1.kj1zl = 0;
gjl1.kj1up = 0;
gjl1.kj1x = 0;
gjl1.kj1tm = 1000;
gjl1.kj1dz = "被打";
gjl1.kj11pw = 30;
gjl1.kj11zl = 2;
gjl1.kj11up = 0;
gjl1.kj11x = 0;
gjl1.kj11tm = 500;
gjl1.kj11dz = "被打";
gjl1.kj12pw = 80;
gjl1.kj12zl = 3;
gjl1.kj12up = -5;
gjl1.kj12x = 0;
gjl1.kj12tm = 0;
gjl1.kj12dz = "击飞";
gjl1.kj2pw = 30;
gjl1.kj2zl = 2;
gjl1.kj2up = 5;
gjl1.kj2x = 1;
gjl1.kj2tm = 1000;
gjl1.kj2dz = "被打";
gjl1.kj21pw = 30;
gjl1.kj21zl = 2;
gjl1.kj21up = 1;
gjl1.kj21x = 1;
gjl1.kj21tm = 1000;
gjl1.kj21dz = "被打";
gjl1.kj22pw = 30;
gjl1.kj22zl = 2;
gjl1.kj22up = 1;
gjl1.kj22x = 1;
gjl1.kj22tm = 1000;
gjl1.kj22dz = "被打";
gjl1.kj23pw = 30;
gjl1.kj23zl = 2;
gjl1.kj23up = 5;
gjl1.kj23x = 5;
gjl1.kj23tm = 1000;
gjl1.kj23dz = "击飞";
gjl1.zh12pw = 0;
gjl1.zh12zl = 0;
gjl1.zh12up = 0;
gjl1.zh12x = 0;
gjl1.zh12tm = 500;
gjl1.zh12dz = "被打";
gjl1.zh1pw = 50;
gjl1.zh1zl = 2;
gjl1.zh1up = 1;
gjl1.zh1x = 15;
gjl1.zh1tm = 500;
gjl1.zh1dz = "被打";
gjl1.zh11pw = 50;
gjl1.zh11zl = 2;
gjl1.zh11up = 5;
gjl1.zh11x = 15;
gjl1.zh11tm = 1000;
gjl1.zh11dz = "击飞";
gjl1.zh2pw = 40;
gjl1.zh2zl = 12;
gjl1.zh2up = 0;
gjl1.zh2x = 0;
gjl1.zh2tm = 1000;
gjl1.zh2dz = "被打";
gjl1.zh21pw = 100;
gjl1.zh21zl = 13;
gjl1.zh21up = 0;
gjl1.zh21x = 0;
gjl1.zh21tm = 1000;
gjl1.zh21dz = "被打";
gjl1.zh22pw = 30;
gjl1.zh22zl = 0;
gjl1.zh22up = 0;
gjl1.zh22x = 20;
gjl1.zh22tm = 0;
gjl1.zh22dz = "击飞";
gjl1.zh3pw = 130;
gjl1.zh3zl = 3;
gjl1.zh3up = 8;
gjl1.zh3x = 0;
gjl1.zh3tm = 0;
gjl1.zh3dz = "击飞";
gjl1.zh31pw = 140;
gjl1.zh31zl = 3;
gjl1.zh31up = 8;
gjl1.zh31x = 8;
gjl1.zh31tm = 0;
gjl1.zh31dz = "击飞";
gjl1.zh32pw = 40;
gjl1.zh32zl = 3;
gjl1.zh32up = -8;
gjl1.zh32x = 8;
gjl1.zh32tm = 500;
gjl1.zh32dz = "被打";
gjl1.zh33pw = 20;
gjl1.zh33zl = 2;
gjl1.zh33up = 0;
gjl1.zh33x = 0;
gjl1.zh33tm = 500;
gjl1.zh33dz = "被打";
gjl1.zh34pw = 20;
gjl1.zh34zl = 2;
gjl1.zh34up = 10;
gjl1.zh34x = 5;
gjl1.zh34tm = 1000;
gjl1.zh34dz = "被打";
gjl1.bs1pw = 100;
gjl1.bs1zl = 3;
gjl1.bs1up = 5;
gjl1.bs1x = 5;
gjl1.bs1tm = 1000;
gjl1.bs1dz = "被打";
gjl1.bspw = 250;
gjl1.bszl = 3;
gjl1.bsup = 0;
gjl1.bsx = 15;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.sbspw = 10;
gjl1.sbszl = 4;
gjl1.sbsup = 0;
gjl1.sbsx = 2;
gjl1.sbstm = 1000;
gjl1.sbsdz = "被打";
gjl1.sbs1pw = 30;
gjl1.sbs1zl = 2;
gjl1.sbs1up = -5;
gjl1.sbs1x = 0;
gjl1.sbs1tm = 1000;
gjl1.sbs1dz = "被打";
gjl1.sbs2pw = 30;
gjl1.sbs2zl = 2;
gjl1.sbs2up = 3;
gjl1.sbs2x = 2;
gjl1.sbs2tm = 1000;
gjl1.sbs2dz = "被打";
gjl1.sbs3pw = 100;
gjl1.sbs3zl = 3;
gjl1.sbs3up = -10;
gjl1.sbs3x = 0;
gjl1.sbs3tm = 0;
gjl1.sbs3dz = "击飞";
gjl1.cbspw = 500;
gjl1.cbszl = 5;
gjl1.cbsup = 0;
gjl1.cbsx = 50;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
