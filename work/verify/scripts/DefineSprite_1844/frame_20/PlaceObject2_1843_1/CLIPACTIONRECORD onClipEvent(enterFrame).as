onClipEvent(enterFrame){
   if(_currentframe == 1)
   {
      if(_root.game.p1.mc.hp > _root.game.p2.mc.hp)
      {
         if(_root.game.p1.mc.hp == _root.maxhp)
         {
            play();
         }
      }
      else if(_root.game.p2.mc.hp == _root.maxhp)
      {
         play();
      }
   }
}
