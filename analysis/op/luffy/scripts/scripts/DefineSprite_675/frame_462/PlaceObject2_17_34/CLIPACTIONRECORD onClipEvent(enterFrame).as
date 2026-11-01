onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bishaSuper())
         {
            _parent.gotoAndPlay("超必杀");
         }
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
         if(magichit3())
         {
            _parent.gotoAndPlay("招3");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招1");
         }
      }
   }
}
