onClipEvent(keyDown){
   if(_parent.cselect == 4)
   {
      if(Key.isDown(_root.a))
      {
         _root.keysound1.start();
         if(cl >= 1)
         {
            cl -= 1;
         }
      }
      if(Key.isDown(_root.d))
      {
         _root.keysound1.start();
         if(cl <= 4)
         {
            cl += 1;
         }
      }
   }
}
