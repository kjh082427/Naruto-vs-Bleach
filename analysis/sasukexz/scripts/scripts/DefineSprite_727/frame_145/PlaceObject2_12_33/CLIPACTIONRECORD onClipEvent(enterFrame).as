onClipEvent(enterFrame){
   if(gameRunning())
   {
      moveX(_parent.speed / 4);
      if(airMagichit())
      {
         _parent.gotoAndPlay("跳招");
      }
   }
}
