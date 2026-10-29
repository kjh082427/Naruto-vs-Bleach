onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
         if(magichit2())
         {
            _parent.gotoAndPlay("招2");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招1");
         }
      }
   }
}
