onClipEvent(enterFrame){
   if(gameRunning())
   {
      if(_parent._parent._xscale < 0)
      {
         _parent._parent._x -= _parent.speed * 3;
      }
      else
      {
         _parent._parent._x += _parent.speed * 3;
      }
   }
}
