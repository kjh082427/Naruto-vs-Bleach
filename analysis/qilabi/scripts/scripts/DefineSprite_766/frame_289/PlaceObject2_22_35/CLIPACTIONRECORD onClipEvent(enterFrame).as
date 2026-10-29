onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(spd);
      if(spd > 3)
      {
         spd--;
      }
   }
}
