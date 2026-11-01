onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed * 2);
      _parent._parent.showdow({G:115});
   }
}
