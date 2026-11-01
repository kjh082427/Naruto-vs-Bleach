onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(4);
      moveY(-5);
      _parent._parent.showdow({B:255});
   }
}
