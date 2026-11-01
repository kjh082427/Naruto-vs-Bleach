if(_root.jie != undefined)
{
   return undefined;
}
_root.jie = function(v)
{
   var _loc5_ = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.,`~!@#$%^&*()_+-=[]{};\':?/".split("");
   var _loc4_ = "";
   var _loc1_ = 0;
   var _loc3_;
   while(_loc1_ < v.length)
   {
      _loc3_ = v.charAt(_loc1_) + v.charAt(_loc1_ + 1);
      _loc4_ += _loc5_[Number(_loc3_)];
      _loc1_ += 2;
   }
   return _loc4_;
};
