onClipEvent(enterFrame){
   if(gameRunning())
   {
      onDashing(3);
      _parent._parent.showdow({R:200,G:200,B:200});
   }
}
