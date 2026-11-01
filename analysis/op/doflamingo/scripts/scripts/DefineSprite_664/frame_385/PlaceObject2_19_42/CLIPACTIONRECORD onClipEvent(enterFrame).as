onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招1");
         }
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍5");
         }
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
      }
   }
}
