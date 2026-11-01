onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(skill1(true))
         {
            _parent.gotoAndPlay("砍技13");
         }
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍技12");
         }
         if(magichit2(true))
         {
            _parent.gotoAndPlay("招2");
         }
      }
   }
}
