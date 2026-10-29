onClipEvent(enterFrame){
   if(_parent._xscale < 0)
   {
      _parent._x -= 20;
   }
   else
   {
      _parent._x += 20;
   }
}
