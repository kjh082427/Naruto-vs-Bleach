onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(skill2(true))
         {
            _parent.gotoAndPlay("砍技21");
         }
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍技21");
         }
      }
   }
}
