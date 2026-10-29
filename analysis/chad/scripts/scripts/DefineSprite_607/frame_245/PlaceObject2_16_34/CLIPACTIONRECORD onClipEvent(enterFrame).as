onClipEvent(enterFrame){
   if(gameRunning())
   {
      if(_parent.kj10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("砍技11");
      }
      else
      {
         moveX(_parent.speed * 3);
      }
   }
}
