onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(hitTest(_root.game["p" + _parent.pn].mc.bdmn) or hitTest(_root.game["p" + _parent.pn].mc.zh1atm) or hitTest(_root.game["p" + _parent.pn].mc.zh2atm) or hitTest(_root.game["p" + _parent.pn].mc.zh3atm) or hitTest(_root.game["p" + _parent.pn].mc.abcd))
      {
         if(played == 0)
         {
            played = 1;
            movspeed = 0;
            gotoAndPlay(5);
         }
      }
      else
      {
         _X = _X + 20;
         _Y = _Y + 20;
      }
   }
}
