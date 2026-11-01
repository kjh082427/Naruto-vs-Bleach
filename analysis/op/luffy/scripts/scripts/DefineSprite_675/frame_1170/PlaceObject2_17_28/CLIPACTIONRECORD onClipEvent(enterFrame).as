onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale < 0)
      {
         _parent._parent._x += _parent.speed * 0.8;
      }
      else
      {
         _parent._parent._x -= _parent.speed * 0.8;
      }
      _parent._parent.showdow({R:255,G:-30});
   }
}
