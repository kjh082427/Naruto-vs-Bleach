function changeNum(shu)
{
   var _loc4_ = 0;
   var _loc2_ = 0;
   var _loc3_ = 0;
   if(shu < 0)
   {
      shu = 0;
   }
   if(shu > 99)
   {
      百._visible = true;
      十._visible = true;
      _loc4_ = Math.floor(shu / 100);
      _loc2_ = Math.floor((shu - _loc4_ * 100) / 10);
      _loc3_ = shu - _loc4_ * 100 - _loc2_ * 10;
   }
   else if(shu > 9)
   {
      百._visible = false;
      十._visible = true;
      _loc2_ = Math.floor(shu / 10);
      _loc3_ = shu - _loc2_ * 10;
   }
   else
   {
      百._visible = false;
      十._visible = false;
      _loc3_ = shu;
   }
   var _loc5_ = _loc4_ + 1;
   var _loc6_ = _loc2_ + 1;
   var _loc7_ = _loc3_ + 1;
   百.gotoAndStop(_loc5_);
   十.gotoAndStop(_loc6_);
   个.gotoAndStop(_loc7_);
}
