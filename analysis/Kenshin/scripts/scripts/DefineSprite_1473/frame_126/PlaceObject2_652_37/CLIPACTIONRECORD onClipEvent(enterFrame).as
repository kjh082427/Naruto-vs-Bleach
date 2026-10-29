onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(_parent.speed);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳砍2");
      }
   }
}
