onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed * 5);
      _parent._parent.showdow({R:-255,G:50,B:255});
   }
}
