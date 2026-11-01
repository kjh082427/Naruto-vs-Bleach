onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(skill2())
         {
            _parent.gotoAndPlay("砍技2");
         }
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍4");
         }
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
      }
   }
}
