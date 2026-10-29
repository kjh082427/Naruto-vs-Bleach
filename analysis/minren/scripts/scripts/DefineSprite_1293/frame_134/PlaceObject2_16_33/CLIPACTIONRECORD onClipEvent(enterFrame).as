onClipEvent(enterFrame){
   if(gameRunning())
   {
      if(moveLeft())
      {
         _parent._parent._x -= _parent.speed;
      }
      if(moveRight())
      {
         _parent._parent._x += _parent.speed;
      }
      if(magichit1())
      {
         _parent.gotoAndPlay("跳招");
      }
   }
   _parent._parent._y -= 1;
}
