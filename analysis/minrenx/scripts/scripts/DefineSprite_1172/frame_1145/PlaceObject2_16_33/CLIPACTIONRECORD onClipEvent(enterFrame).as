onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y += 30;
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("空中必杀2");
      }
   }
}
