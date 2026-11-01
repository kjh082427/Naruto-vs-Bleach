onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(magichit3())
         {
            _parent.gotoAndPlay("招33");
         }
         if(magichit2())
         {
            _parent.gotoAndPlay("招34");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招32");
         }
      }
   }
}
