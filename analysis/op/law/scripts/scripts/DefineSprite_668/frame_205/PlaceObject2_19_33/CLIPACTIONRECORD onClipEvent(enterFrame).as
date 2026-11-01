onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(10);
      moveY(-20);
      _parent._parent.showdow({R:-67,G:-169,B:-255});
   }
}
