function select(id)
{
   if(id < 0)
   {
      id = 4;
   }
   if(id > 4)
   {
      id = 0;
   }
   arrowmc._y = _this["b" + id]._y;
   _curid = id;
   var _loc2_ = 0;
   while(_loc2_ < 5)
   {
      _this["b" + _loc2_].gotoAndStop(1);
      _loc2_ = _loc2_ + 1;
   }
   _this["b" + id].gotoAndStop(2);
   _root.keysound1.start();
}
function goSelect(id)
{
   if(id < 0 || id > 4)
   {
      return undefined;
   }
   Key.removeListener(kl);
   _root.keysound2.start();
   switch(id)
   {
      case 0:
         _root.modo = 1;
         _root.p1cpu = false;
         _root.p2cpu = true;
         _root.gotoAndStop("选人画面");
         break;
      case 1:
         _root.txtst = 0;
         _root.modo = 2;
         _root.p1cpu = false;
         _root.p2cpu = true;
         _root.gotoAndStop("选人画面");
         break;
      case 2:
         _root.p1cpu = false;
         _root.p2cpu = false;
         _root.modo = 3;
         _root.gotoAndStop("选人画面");
         break;
      case 3:
         _root.txtst = 0;
         _root.modo = 4;
         _root.p1cpu = false;
         _root.p2cpu = false;
         _root.gotoAndStop("选人画面");
         break;
      case 4:
         _root.gotoAndStop("游戏设置");
      default:
         return;
   }
}
stop();
_this = this;
var i = 0;
while(i < 5)
{
   _this["b" + i].gotoAndStop(1);
   _this["b" + i].id = i;
   _this["b" + i].onRollOver = function()
   {
      var _loc2_ = this.id;
      select(_loc2_);
   };
   _this["b" + i].onRelease = function()
   {
      var _loc2_ = this.id;
      goSelect(_loc2_);
   };
   i++;
}
var _curid = 0;
var kl = new Object();
kl.onKeyDown = function()
{
   if(Key.isDown(_root.w))
   {
      select(_curid - 1);
   }
   if(Key.isDown(_root.s))
   {
      select(_curid + 1);
   }
   if(Key.isDown(_root.j))
   {
      goSelect(_curid);
   }
};
Key.addListener(kl);
