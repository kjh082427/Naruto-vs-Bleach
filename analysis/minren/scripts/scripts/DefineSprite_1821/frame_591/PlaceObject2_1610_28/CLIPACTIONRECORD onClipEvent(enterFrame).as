onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(played == 1)
      {
         return undefined;
      }
      if(hitTest(_root.game["p" + _parent.pn].mc.bdmn) || hitTest(_root.game["p" + _parent.pn].mc.mian))
      {
         if(played == 0)
         {
            played = 1;
            movspeed = 0;
            gotoAndPlay(2);
         }
      }
      else
      {
         _X = _X + movspeed;
      }
   }
}
