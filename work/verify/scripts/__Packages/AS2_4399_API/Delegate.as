class AS2_4399_API.Delegate extends Object
{
   var func;
   function Delegate(f)
   {
      super();
      this.func = f;
   }
   static function create(obj, func)
   {
      var _loc2_ = function()
      {
         var _loc2_ = arguments.callee.target;
         var _loc3_ = arguments.callee.func;
         return _loc3_.apply(_loc2_,arguments);
      };
      _loc2_.target = obj;
      _loc2_.func = func;
      return _loc2_;
   }
   function createDelegate(obj)
   {
      return create(obj,this.func);
   }
}
