onClipEvent(enterFrame){
   if(gameRunning())
   {
      moveX(_parent.speed);
      moveY(-5);
   }
}
