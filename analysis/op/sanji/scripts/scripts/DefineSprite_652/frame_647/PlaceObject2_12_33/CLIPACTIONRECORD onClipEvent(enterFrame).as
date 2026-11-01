onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(10);
      moveX(10);
      _parent._parent.showdow({R:255});
   }
}
