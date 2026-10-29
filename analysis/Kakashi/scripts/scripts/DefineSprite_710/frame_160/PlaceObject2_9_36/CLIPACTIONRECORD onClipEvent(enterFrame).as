onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y -= 1;
      if(_parent._parent._xscale > 0)
      {
         _parent._parent._x -= 1;
      }
      else
      {
         _parent._parent._x += 1;
      }
   }
}
