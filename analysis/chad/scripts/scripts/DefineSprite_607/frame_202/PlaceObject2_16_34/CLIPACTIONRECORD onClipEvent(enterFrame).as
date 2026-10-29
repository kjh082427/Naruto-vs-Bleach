onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale < 0)
      {
         _parent._parent._x -= _parent.speed * 1.5;
      }
      else
      {
         _parent._parent._x += _parent.speed * 1.5;
      }
   }
}
