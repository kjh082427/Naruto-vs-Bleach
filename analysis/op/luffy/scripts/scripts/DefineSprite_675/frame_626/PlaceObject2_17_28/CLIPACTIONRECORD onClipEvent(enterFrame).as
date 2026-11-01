onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(15);
      moveX(15);
      _parent._parent.showdow({R:255,G:-30});
   }
}
