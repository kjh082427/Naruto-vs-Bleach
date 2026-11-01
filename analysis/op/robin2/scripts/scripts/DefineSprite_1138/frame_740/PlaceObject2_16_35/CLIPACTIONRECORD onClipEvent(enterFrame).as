onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(20);
      moveY(15);
      _parent._parent.showdow({B:255});
   }
}
