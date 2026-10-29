onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y += 32;
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("破中击！");
      }
   }
}
