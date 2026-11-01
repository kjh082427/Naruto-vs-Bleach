onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(!holdJ())
      {
         _parent.gotoAndPlay("砍技11");
      }
   }
}
