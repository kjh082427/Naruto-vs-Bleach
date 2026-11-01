onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed);
      moveY(10);
      _parent._parent.showdow({B:255});
   }
}
