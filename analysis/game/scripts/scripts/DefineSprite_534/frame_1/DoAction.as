function showStart()
{
   loading._visible = false;
   _root.play();
}
stop();
startBtn._visible = false;
var persent = 0;
onEnterFrame = function()
{
   var _loc2_ = _root.getBytesLoaded() / _root.getBytesTotal() * 100;
   if(persent < _loc2_)
   {
      persent += 2;
   }
   bar._xscale = persent;
   if(persent >= 100)
   {
      delete onEnterFrame;
   }
};
