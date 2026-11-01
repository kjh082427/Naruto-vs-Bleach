onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(skill2())
         {
            _parent.gotoAndPlay("砍技2");
         }
         if(bishaUP())
         {
            _parent.gotoAndPlay("上必杀");
         }
         if(jump())
         {
            _parent.gotoAndPlay("跳");
         }
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
      }
   }
}
