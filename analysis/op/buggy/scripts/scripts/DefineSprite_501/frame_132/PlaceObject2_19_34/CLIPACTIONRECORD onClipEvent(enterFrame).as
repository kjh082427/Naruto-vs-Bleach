onClipEvent(enterFrame){
   if(gameRunning())
   {
      moveX(_parent.speed);
      moveY(_parent.speed * 1.5);
   }
}
