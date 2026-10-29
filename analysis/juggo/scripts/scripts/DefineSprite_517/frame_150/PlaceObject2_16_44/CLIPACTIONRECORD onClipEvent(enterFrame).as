onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale > 0)
      {
         _parent._parent._x += 4;
      }
      else
      {
         _parent._parent._x -= 4;
      }
      _parent._parent._y -= 2;
   }
}
