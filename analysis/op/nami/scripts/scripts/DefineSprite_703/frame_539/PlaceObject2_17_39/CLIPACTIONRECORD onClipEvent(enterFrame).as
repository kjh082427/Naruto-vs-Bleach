onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed * 2);
      moveY(12);
      _parent._parent.showdow({R:60,B:255});
   }
}
