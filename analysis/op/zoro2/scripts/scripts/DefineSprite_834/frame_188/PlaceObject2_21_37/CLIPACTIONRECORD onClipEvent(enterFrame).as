onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(10);
      moveY(-10);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
      }
      _parent._parent.showdow({G:115});
   }
}
