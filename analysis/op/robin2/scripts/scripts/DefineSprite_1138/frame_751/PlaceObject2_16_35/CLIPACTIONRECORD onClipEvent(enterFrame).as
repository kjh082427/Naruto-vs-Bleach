onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(20);
      moveY(-15);
      if(_parent.touchFloor)
      {
         _parent.gotoAndPlay("招30");
      }
      _parent._parent.showdow({B:255});
   }
}
