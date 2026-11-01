onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(- _parent.speed);
      _parent._parent.showdow({R:200,G:200,B:200});
   }
}
