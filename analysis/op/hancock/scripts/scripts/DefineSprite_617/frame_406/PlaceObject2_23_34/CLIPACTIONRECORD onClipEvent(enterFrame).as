onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍技12");
         }
         if(skill2())
         {
            _parent.gotoAndPlay("砍技2");
         }
      }
   }
}
