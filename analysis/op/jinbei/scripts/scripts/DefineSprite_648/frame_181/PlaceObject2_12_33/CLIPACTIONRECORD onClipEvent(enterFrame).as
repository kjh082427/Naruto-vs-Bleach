onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(10);
      moveY(-20);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
      }
      _parent._parent.showdow({R:-255,G:50,B:255});
   }
}
