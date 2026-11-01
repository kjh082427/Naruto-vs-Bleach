onClipEvent(enterFrame){
   if(gameRunning())
   {
      if(bishaAir())
      {
         _parent.gotoAndPlay("空中必杀");
      }
      if(airMagichit())
      {
         _parent.gotoAndPlay("跳招");
      }
      if(nornalhit(true))
      {
         _parent.gotoAndPlay("跳砍3");
      }
      moveX(_parent.speed / 2);
   }
}
