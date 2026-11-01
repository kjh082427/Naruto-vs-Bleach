onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed * 4);
      _parent._parent.showdow({R:255,G:-30});
   }
}
