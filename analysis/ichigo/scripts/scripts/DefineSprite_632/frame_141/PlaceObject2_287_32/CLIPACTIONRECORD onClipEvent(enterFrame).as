onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
         return undefined;
      }
      moveX(30);
      moveY(-20);
   }
}
