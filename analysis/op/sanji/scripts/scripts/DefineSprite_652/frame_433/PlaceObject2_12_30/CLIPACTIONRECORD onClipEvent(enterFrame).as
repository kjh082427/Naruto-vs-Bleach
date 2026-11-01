onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(5);
      moveY(20);
      _parent._parent.showdow({R:200});
   }
}
