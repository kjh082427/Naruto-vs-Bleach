onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed * 6);
      _parent._parent.showdow();
   }
}
