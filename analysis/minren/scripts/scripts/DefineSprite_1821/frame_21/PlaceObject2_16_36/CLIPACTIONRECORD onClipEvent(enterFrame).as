onClipEvent(enterFrame){
   if(gameRunning())
   {
      _parent._parent._x += _parent.speed * 3 * _parent._parent.scale_X;
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
