onClipEvent(keyDown){
   if(!_parent.skipAble)
   {
      return undefined;
   }
   if(Key.isDown(_root.j))
   {
      stopAllSounds();
      _parent.gotoAndPlay("skip");
   }
   if(Key.isDown(_root.N1))
   {
      stopAllSounds();
      _parent.gotoAndPlay("skip");
   }
}
