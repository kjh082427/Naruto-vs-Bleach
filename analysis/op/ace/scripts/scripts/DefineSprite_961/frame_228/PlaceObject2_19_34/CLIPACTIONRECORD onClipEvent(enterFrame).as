onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(-20);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
      }
      _parent._parent.showdow({R:255});
   }
}
