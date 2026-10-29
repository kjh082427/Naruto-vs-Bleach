onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y += _parent.speed;
      if(_parent.touchFloor)
      {
         _parent.gotoAndPlay("超必杀2");
      }
   }
}
