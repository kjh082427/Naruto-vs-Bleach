onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(7);
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(magichit3())
         {
            _parent.gotoAndPlay("招33");
         }
      }
   }
}
