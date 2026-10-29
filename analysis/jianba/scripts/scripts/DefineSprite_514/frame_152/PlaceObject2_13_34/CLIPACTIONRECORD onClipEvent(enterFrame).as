onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y += 20;
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招3");
      }
   }
}
