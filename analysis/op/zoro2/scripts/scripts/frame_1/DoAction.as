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
var heavy = 2;
var gjl1 = [];
gjl1.tkpw = 40;
gjl1.tkzl = 1;
gjl1.tkup = 0;
gjl1.tkx = 4;
gjl1.tktm = 500;
gjl1.tkdz = "被打";
gjl1.tk1pw = 80;
gjl1.tk1zl = 6;
gjl1.tk1up = 0;
gjl1.tk1x = 15;
gjl1.tk1tm = 0;
gjl1.tk1dz = "击飞";
gjl1.tz1pw = 20;
gjl1.tz1zl = 1;
gjl1.tz1up = -5;
gjl1.tz1x = 5;
gjl1.tz1tm = 500;
gjl1.tz1dz = "被打";
gjl1.tzpw = 70;
gjl1.tzzl = 1;
gjl1.tzup = 6;
gjl1.tzx = 0;
gjl1.tztm = 0;
gjl1.tzdz = "击飞";
gjl1.k1pw = 20;
gjl1.k1zl = 2;
gjl1.k1up = 0;
gjl1.k1x = 4;
gjl1.k1tm = 400;
gjl1.k1dz = "被打";
gjl1.k2pw = 40;
gjl1.k2zl = 1;
gjl1.k2up = 0;
gjl1.k2x = 3;
gjl1.k2tm = 500;
gjl1.k2dz = "被打";
gjl1.k3pw = 50;
gjl1.k3zl = 3;
gjl1.k3up = 0;
gjl1.k3x = 3;
gjl1.k3tm = 600;
gjl1.k3dz = "被打";
gjl1.k4pw = 60;
gjl1.k4zl = 6;
gjl1.k4up = 6;
gjl1.k4x = 2;
gjl1.k4tm = 600;
gjl1.k4dz = "被打";
gjl1.kj1pw = 60;
gjl1.kj1zl = 6;
gjl1.kj1up = 0;
gjl1.kj1x = 5;
gjl1.kj1tm = 500;
gjl1.kj1dz = "被打";
gjl1.kj11pw = 60;
gjl1.kj11zl = 6;
gjl1.kj11up = 0;
gjl1.kj11x = 5;
gjl1.kj11tm = 500;
gjl1.kj11dz = "被打";
gjl1.kj12pw = 80;
gjl1.kj12zl = 6;
gjl1.kj12up = 0;
gjl1.kj12x = 15;
gjl1.kj12tm = 0;
gjl1.kj12dz = "击飞";
gjl1.kj2pw = 13;
gjl1.kj2zl = 1;
gjl1.kj2up = 4;
gjl1.kj2x = 0;
gjl1.kj2tm = 500;
gjl1.kj2dz = "被打";
gjl1.kj21pw = 13;
gjl1.kj21zl = 1;
gjl1.kj21up = 0;
gjl1.kj21x = 0;
gjl1.kj21tm = 500;
gjl1.kj21dz = "被打";
gjl1.kj22pw = 40;
gjl1.kj22zl = 6;
gjl1.kj22up = -15;
gjl1.kj22x = 0;
gjl1.kj22tm = 0;
gjl1.kj22dz = "击飞";
gjl1.zh1pw = 100;
gjl1.zh1zl = 6;
gjl1.zh1up = 0;
gjl1.zh1x = 10;
gjl1.zh1tm = 0;
gjl1.zh1dz = "击飞";
gjl1.zh2pw = 150;
gjl1.zh2zl = 15;
gjl1.zh2up = 0;
gjl1.zh2x = 20;
gjl1.zh2tm = 0;
gjl1.zh2dz = "击飞";
gjl1.zh3pw = 160;
gjl1.zh3zl = 6;
gjl1.zh3up = 2;
gjl1.zh3x = 1;
gjl1.zh3tm = 0;
gjl1.zh3dz = "击飞";
gjl1.bs1pw = 0;
gjl1.bs1zl = 0;
gjl1.bs1up = 0;
gjl1.bs1x = 0;
gjl1.bs1tm = 5000;
gjl1.bs1dz = "被打";
gjl1.bspw = 300;
gjl1.bszl = 6;
gjl1.bsup = 3;
gjl1.bsx = 0;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.kbs1pw = 20;
gjl1.kbs1zl = 1;
gjl1.kbs1up = -10;
gjl1.kbs1x = 0;
gjl1.kbs1tm = 500;
gjl1.kbs1dz = "被打";
gjl1.kbs2pw = 60;
gjl1.kbs2zl = 6;
gjl1.kbs2up = 0;
gjl1.kbs2x = 0;
gjl1.kbs2tm = 500;
gjl1.kbs2dz = "被打";
gjl1.kbspw = 60;
gjl1.kbszl = 5;
gjl1.kbsup = 5;
gjl1.kbsx = 10;
gjl1.kbstm = 0;
gjl1.kbsdz = "击飞";
gjl1.sbs2pw = 40;
gjl1.sbs2zl = 9;
gjl1.sbs2up = 2;
gjl1.sbs2x = 0;
gjl1.sbs2tm = 500;
gjl1.sbs2dz = "被打";
gjl1.sbspw = 15;
gjl1.sbszl = 1;
gjl1.sbsup = 2;
gjl1.sbsx = 0;
gjl1.sbstm = 500;
gjl1.sbsdz = "被打";
gjl1.sbs1pw = 15;
gjl1.sbs1zl = 1;
gjl1.sbs1up = 5;
gjl1.sbs1x = 5;
gjl1.sbs1tm = 0;
gjl1.sbs1dz = "击飞";
gjl1.cbs1pw = 30;
gjl1.cbs1zl = 4;
gjl1.cbs1up = 0;
gjl1.cbs1x = 18;
gjl1.cbs1tm = 1000;
gjl1.cbs1dz = "被打";
gjl1.cbspw = 100;
gjl1.cbszl = 15;
gjl1.cbsup = 20;
gjl1.cbsx = 5;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
