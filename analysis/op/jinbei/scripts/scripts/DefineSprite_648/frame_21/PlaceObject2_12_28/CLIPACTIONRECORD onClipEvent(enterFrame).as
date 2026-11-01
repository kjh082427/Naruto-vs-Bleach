onClipEvent(enterFrame){
   if(gameRunning())
   {
      onDashing(3.5);
      _parent._parent.showdow({R:-255,G:50,B:255});
   }
}
