onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(-5);
      moveX(5);
      _parent._parent.showdow({R:255});
   }
}
