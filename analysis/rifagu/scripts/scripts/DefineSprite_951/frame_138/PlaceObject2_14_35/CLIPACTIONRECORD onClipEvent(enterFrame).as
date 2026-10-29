onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y += _parent.speed * 3;
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
      }
   }
}
