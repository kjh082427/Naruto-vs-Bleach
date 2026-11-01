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
gjl1.tktm = 300;
gjl1.tkdz = "被打";
gjl1.tk1pw = 80;
gjl1.tk1zl = 6;
gjl1.tk1up = -8;
gjl1.tk1x = 10;
gjl1.tk1tm = 0;
gjl1.tk1dz = "击飞";
gjl1.tzpw = 120;
gjl1.tzzl = 6;
gjl1.tzup = -10;
gjl1.tzx = 2;
gjl1.tztm = 500;
gjl1.tzdz = "击飞";
gjl1.k1pw = 30;
gjl1.k1zl = 1;
gjl1.k1up = 0;
gjl1.k1x = 3;
gjl1.k1tm = 400;
gjl1.k1dz = "被打";
gjl1.k2pw = 40;
gjl1.k2zl = 1;
gjl1.k2up = 0;
gjl1.k2x = 4;
gjl1.k2tm = 500;
gjl1.k2dz = "被打";
gjl1.k3pw = 60;
gjl1.k3zl = 6;
gjl1.k3up = 7;
gjl1.k3x = 5;
gjl1.k3tm = 600;
gjl1.k3dz = "被打";
gjl1.kj1pw = 50;
gjl1.kj1zl = 16;
gjl1.kj1up = 0;
gjl1.kj1x = 5;
gjl1.kj1tm = 600;
gjl1.kj1dz = "被打";
gjl1.kj11pw = 30;
gjl1.kj11zl = 1;
gjl1.kj11up = 0;
gjl1.kj11x = 5;
gjl1.kj11tm = 500;
gjl1.kj11dz = "被打";
gjl1.kj12pw = 70;
gjl1.kj12zl = 6;
gjl1.kj12up = -5;
gjl1.kj12x = 10;
gjl1.kj12tm = 0;
gjl1.kj12dz = "击飞";
gjl1.kj2pw = 25;
gjl1.kj2zl = 1;
gjl1.kj2up = 7;
gjl1.kj2x = 4;
gjl1.kj2tm = 500;
gjl1.kj2dz = "被打";
gjl1.zh1pw = 80;
gjl1.zh1zl = 5;
gjl1.zh1up = 0;
gjl1.zh1x = 10;
gjl1.zh1tm = 0;
gjl1.zh1dz = "击飞";
gjl1.zh21pw = 30;
gjl1.zh21zl = 1;
gjl1.zh21up = 0;
gjl1.zh21x = 9;
gjl1.zh21tm = 500;
gjl1.zh21dz = "被打";
gjl1.zh2pw = 60;
gjl1.zh2zl = 6;
gjl1.zh2up = 0;
gjl1.zh2x = 2;
gjl1.zh2tm = 400;
gjl1.zh2dz = "被打";
gjl1.zh31pw = 45;
gjl1.zh31zl = 1;
gjl1.zh31up = 3;
gjl1.zh31x = 0;
gjl1.zh31tm = 500;
gjl1.zh31dz = "被打";
gjl1.zh3pw = 45;
gjl1.zh3zl = 1;
gjl1.zh3up = 5;
gjl1.zh3x = 0;
gjl1.zh3tm = 0;
gjl1.zh3dz = "击飞";
gjl1.bspw = 280;
gjl1.bszl = 5;
gjl1.bsup = 0;
gjl1.bsx = 20;
gjl1.bstm = 0;
gjl1.bsdz = "击飞";
gjl1.sbspw = 250;
gjl1.sbszl = 6;
gjl1.sbsup = 10;
gjl1.sbsx = 3;
gjl1.sbstm = 0;
gjl1.sbsdz = "击飞";
gjl1.cbs1pw = 100;
gjl1.cbs1zl = 6;
gjl1.cbs1up = 5;
gjl1.cbs1x = 5;
gjl1.cbs1tm = 0;
gjl1.cbs1dz = "被打";
gjl1.cbspw = 150;
gjl1.cbszl = 5;
gjl1.cbsup = 20;
gjl1.cbsx = 20;
gjl1.cbstm = 0;
gjl1.cbsdz = "击飞";
