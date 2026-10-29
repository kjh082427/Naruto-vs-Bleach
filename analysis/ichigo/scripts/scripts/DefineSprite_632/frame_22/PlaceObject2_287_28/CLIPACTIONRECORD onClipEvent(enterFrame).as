onClipEvent(enterFrame){
   if(gameRunning())
   {
      if(_parent._parent._xscale < 0)
      {
         _parent._parent._x -= _parent.speed * 4;
      }
      else
      {
         _parent._parent._x += _parent.speed * 4;
      }
      if(bishaUP())
      {
         _parent.gotoAndPlay("上必杀");
      }
      if(bishaSuper())
      {
         _parent.gotoAndPlay("超必杀");
      }
      if(bisha())
      {
         _parent.gotoAndPlay("必杀");
      }
   }
}
