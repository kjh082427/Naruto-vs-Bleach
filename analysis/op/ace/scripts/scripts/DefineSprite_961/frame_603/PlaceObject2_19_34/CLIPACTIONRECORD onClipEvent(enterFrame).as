onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(!holdU())
      {
         _parent.gotoAndPlay("招21");
      }
   }
}
