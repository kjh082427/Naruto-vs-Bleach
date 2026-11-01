onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bishaSuper())
         {
            _parent.gotoAndPlay("超必杀");
         }
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍4");
         }
      }
   }
}
