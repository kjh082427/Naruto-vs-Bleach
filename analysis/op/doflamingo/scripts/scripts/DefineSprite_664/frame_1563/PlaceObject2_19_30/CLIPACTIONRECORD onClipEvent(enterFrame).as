onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale < 0)
      {
         _parent._parent._x += _parent.speed;
      }
      else
      {
         _parent._parent._x -= _parent.speed;
      }
      _parent._parent.showdow({R:255,G:255,B:255});
   }
}
