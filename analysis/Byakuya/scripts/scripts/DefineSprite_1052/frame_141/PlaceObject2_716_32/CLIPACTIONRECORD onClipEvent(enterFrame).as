onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(-15);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("砍技1");
      }
   }
}
