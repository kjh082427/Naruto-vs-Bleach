onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bishaUP())
         {
            _parent.gotoAndPlay("上必杀");
         }
         if(magichit2())
         {
            _parent.gotoAndPlay("招2");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招1");
         }
         if(nornalhit(true))
         {
            _parent.gotoAndPlay("砍技12");
         }
         if(dohide())
         {
            _parent.gotoAndPlay("起身");
         }
      }
   }
}
