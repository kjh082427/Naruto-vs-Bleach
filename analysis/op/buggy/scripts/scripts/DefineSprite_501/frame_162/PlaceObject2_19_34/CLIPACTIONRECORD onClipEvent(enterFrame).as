onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(15);
      moveY(-20);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
      }
      _parent._parent.showdow({R:200,G:200,B:200});
   }
}
