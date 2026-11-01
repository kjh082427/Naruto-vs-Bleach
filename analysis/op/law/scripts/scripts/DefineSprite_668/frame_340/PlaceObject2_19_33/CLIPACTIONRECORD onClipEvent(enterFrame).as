onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(magichit3())
         {
            _parent.gotoAndPlay("招3");
         }
         if(bishaUP())
         {
            _parent.gotoAndPlay("上必杀");
         }
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
         if(jump())
         {
            _parent.gotoAndPlay("跳");
         }
      }
   }
}
