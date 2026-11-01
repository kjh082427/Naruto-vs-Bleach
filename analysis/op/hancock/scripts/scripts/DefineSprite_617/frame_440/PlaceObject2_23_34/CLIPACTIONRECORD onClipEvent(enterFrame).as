onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍技13");
         }
         if(bishaSuper())
         {
            _parent.gotoAndPlay("超必杀");
         }
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
      }
   }
}
