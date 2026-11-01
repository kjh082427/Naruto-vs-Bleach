onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed * 0.5);
      _parent._parent.showdow({R:255});
   }
}
