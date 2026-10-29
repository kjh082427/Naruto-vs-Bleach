onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(15);
      moveY(-25);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("超必杀3");
      }
   }
}
