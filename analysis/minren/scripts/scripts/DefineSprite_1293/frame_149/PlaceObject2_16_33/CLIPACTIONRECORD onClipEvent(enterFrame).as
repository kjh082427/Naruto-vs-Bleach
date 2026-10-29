onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale < 0)
      {
         _parent._parent._x -= _parent.speed * 2;
      }
      else
      {
         _parent._parent._x += _parent.speed * 2;
      }
      _parent._parent._y += _parent.speed;
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("落地");
      }
   }
}
