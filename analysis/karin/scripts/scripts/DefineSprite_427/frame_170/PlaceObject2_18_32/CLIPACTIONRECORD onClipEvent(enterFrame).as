onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y -= 8;
      if(_parent._parent._xscale > 0)
      {
         _parent._parent._x -= 2;
      }
      else
      {
         _parent._parent._x += 2;
      }
   }
}
