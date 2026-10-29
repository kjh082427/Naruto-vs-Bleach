onClipEvent(keyDown){
   if(_parent.cselect == 3)
   {
      if(Key.isDown(_root.a))
      {
         if(cl >= 1)
         {
            _root.keysound1.start();
            cl -= 1;
         }
      }
      if(Key.isDown(_root.d))
      {
         if(cl <= 3)
         {
            _root.keysound1.start();
            cl += 1;
         }
      }
   }
}
