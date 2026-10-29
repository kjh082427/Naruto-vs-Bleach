onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(airMagichit())
         {
            _parent.gotoAndPlay("跳招");
         }
         if(bishaAir())
         {
            _parent.gotoAndPlay("空中必杀");
         }
      }
      moveY(5);
   }
}
