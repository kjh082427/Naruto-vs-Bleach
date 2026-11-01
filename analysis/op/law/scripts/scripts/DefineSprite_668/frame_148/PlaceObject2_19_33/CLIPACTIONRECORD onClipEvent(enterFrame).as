onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed / 2);
      moveY(5);
      _parent._parent.showdow({R:-67,G:-169,B:-255});
   }
}
