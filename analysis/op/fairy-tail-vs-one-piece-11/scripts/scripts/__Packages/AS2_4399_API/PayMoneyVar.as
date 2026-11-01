class AS2_4399_API.PayMoneyVar
{
   var _money;
   static var instance;
   function PayMoneyVar()
   {
      if(instance != null)
      {
         throw new Error("只能实例一次！");
      }
   }
   static function getInstance()
   {
      if(instance == null)
      {
         instance = new AS2_4399_API.PayMoneyVar();
      }
      return instance;
   }
   function set money(varMoney)
   {
      varMoney = Math.abs(varMoney);
      var _loc2_ = {value:varMoney};
      _loc2_ = {value:_loc2_.value};
      this._money = _loc2_;
   }
   function get money()
   {
      if(this._money == null)
      {
         return 0;
      }
      var _loc2_ = new Object();
      _loc2_.value = this._money.value;
      return Number(_loc2_.value);
   }
}
