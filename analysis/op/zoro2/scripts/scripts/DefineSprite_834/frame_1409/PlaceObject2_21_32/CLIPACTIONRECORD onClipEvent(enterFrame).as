onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX((- _parent.speed) * 0.8);
      _parent._parent.showdow({G:115});
   }
}
