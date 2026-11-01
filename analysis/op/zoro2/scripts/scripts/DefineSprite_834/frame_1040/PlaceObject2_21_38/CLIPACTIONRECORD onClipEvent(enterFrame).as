onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(-15);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("空中必杀2");
      }
      _parent._parent.showdow({G:115});
   }
}
