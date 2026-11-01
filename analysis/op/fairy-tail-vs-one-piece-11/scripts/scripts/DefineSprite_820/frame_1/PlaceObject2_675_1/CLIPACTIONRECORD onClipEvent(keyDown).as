onClipEvent(keyDown){
   if(_parent.cselect == 2)
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
         if(cl <= 5)
         {
            cl += 1;
         }
      }
   }
}
