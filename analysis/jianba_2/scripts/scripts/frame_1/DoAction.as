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
gjl.atm1pw = 200;
gjl.atm1zl = 15;
gjl.atm1up = 0;
gjl.atm1x = 15;
gjl.atm1tm = 0;
gjl.atm1dz = "击飞";
