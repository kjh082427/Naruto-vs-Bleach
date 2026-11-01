onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(magichit2())
         {
            _parent.gotoAndPlay("招22");
         }
      }
   }
}
