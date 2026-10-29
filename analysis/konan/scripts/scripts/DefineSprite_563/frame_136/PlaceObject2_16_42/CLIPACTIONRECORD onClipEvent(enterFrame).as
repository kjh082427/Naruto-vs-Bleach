onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(moveLeft())
         {
            _parent._parent._x -= _parent.speed;
         }
         if(moveRight())
         {
            _parent._parent._x += _parent.speed;
         }
      }
   }
}
