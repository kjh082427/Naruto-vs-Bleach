onClipEvent(enterFrame){
   if(gameRunning())
   {
      if(_parent.zh20atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("砍41");
      }
   }
}
