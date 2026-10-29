onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed);
      _parent._parent._y -= 2;
   }
}
