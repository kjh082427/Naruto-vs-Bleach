onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y += 10;
      if(_parent.nn >= 1)
      {
         if(_parent.touch == true)
         {
            _parent.gotoAndPlay("跳招2");
         }
      }
   }
}
