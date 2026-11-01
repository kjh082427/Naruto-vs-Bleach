onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
         if(skill1())
         {
            _parent.gotoAndPlay("砍技13");
         }
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍技13");
         }
         if(magichit2())
         {
            _parent.gotoAndPlay("招2");
         }
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
      }
   }
}
