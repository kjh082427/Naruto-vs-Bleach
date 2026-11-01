onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(15);
      moveY(15);
      _parent._parent.showdow({R:255});
   }
}
