onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._x += 8 * (_parent._parent._xscale <= 0 ? -1 : 1);
      _parent._parent._y += 10;
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
      }
   }
}
