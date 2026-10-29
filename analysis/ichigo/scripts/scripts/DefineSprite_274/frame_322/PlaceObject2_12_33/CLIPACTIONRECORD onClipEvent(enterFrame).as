onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bishaUP())
         {
            _parent.gotoAndPlay("上必杀");
         }
         if(magichit3())
         {
            _parent.gotoAndPlay("招3");
         }
      }
   }
}
