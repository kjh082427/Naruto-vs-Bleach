onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX((- _parent.speed) * 1.5);
      _parent._parent.showdow({R:193,G:117});
   }
}
