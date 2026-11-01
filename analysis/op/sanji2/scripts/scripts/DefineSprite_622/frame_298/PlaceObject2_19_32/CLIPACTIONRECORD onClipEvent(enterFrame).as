onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(8);
      moveY(10);
      _parent._parent.showdow({B:255});
   }
}
