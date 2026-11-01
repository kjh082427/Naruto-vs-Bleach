onClipEvent(enterFrame){
   if(gameRunning())
   {
      onDashing(6.5);
      _parent._parent.showdow({R:255,G:255,B:255});
   }
}
