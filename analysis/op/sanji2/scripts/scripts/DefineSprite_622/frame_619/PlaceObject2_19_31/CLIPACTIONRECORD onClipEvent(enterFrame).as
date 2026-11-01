onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("空中必杀2");
         return undefined;
      }
      moveY(-20);
      _parent._parent.showdow({B:255});
   }
}
