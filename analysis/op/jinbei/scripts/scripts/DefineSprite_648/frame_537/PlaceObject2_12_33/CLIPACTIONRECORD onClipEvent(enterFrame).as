onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(20);
      moveX(18);
      _parent._parent.showdow({R:-255,G:50,B:255});
   }
}
