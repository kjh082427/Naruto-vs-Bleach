onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(5);
      moveY(5);
      _parent._parent.showdow({R:255});
   }
}
