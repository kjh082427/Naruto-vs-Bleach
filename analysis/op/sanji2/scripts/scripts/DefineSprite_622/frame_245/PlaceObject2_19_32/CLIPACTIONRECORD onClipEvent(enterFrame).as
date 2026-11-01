onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bishaUP())
         {
            _parent.gotoAndPlay("上必杀");
         }
         if(magichit3(true))
         {
            _parent.gotoAndPlay("招31");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招1");
         }
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
      }
   }
}
