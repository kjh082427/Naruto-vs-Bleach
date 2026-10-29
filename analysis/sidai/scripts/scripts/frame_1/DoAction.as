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
var inited;
var _this = this;
var bs = 0;
var hited = 0;
var attacking = false;
_X = _Y = -200;
if(!inited)
{
   trace("fz inited");
   inited = true;
   _this.sn = _this._name != "p1fz" ? 2 : 1;
   _this.pn = _this.sn != 1 ? 1 : 2;
}
var _si = 0;
stop();
var gjl = [];
gjl.atm1pw = 50;
gjl.atm1zl = 5;
gjl.atm1up = -10;
gjl.atm1x = 0;
gjl.atm1tm = 0;
gjl.atm1dz = "击飞";
gjl.atm3pw = 50;
gjl.atm3zl = 3;
gjl.atm3up = 10;
gjl.atm3x = 5;
gjl.atm3tm = 1000;
gjl.atm3dz = "被打";
gjl.atm5pw = 10;
gjl.atm5zl = 4;
gjl.atm5up = -1;
gjl.atm5x = 0;
gjl.atm5tm = 300;
gjl.atm5dz = "被打";
gjl.atm2pw = 50;
gjl.atm2zl = 3;
gjl.atm2up = 0;
gjl.atm2x = 10;
gjl.atm2tm = 1000;
gjl.atm2dz = "被打";
gjl.atm4pw = 50;
gjl.atm4zl = 16;
gjl.atm4up = 0;
gjl.atm4x = -8;
gjl.atm4tm = 1000;
gjl.atm4dz = "被打";
