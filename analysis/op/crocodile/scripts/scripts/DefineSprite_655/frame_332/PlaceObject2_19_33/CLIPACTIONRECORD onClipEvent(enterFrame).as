onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍技12");
         }
         if(bishaUP())
         {
            _parent.gotoAndPlay("上必杀");
         }
         if(bishaSuper())
         {
            _parent.gotoAndPlay("超必杀");
         }
      }
   }
}
