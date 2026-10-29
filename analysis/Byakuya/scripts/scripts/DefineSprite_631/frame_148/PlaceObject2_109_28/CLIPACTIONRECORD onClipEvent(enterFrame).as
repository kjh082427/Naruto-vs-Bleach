onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(hitTest(_root.game["p" + _parent.pn].mc.bdmn) || hitTest(_root.game["p" + _parent.pn].mc.zh1atm) || hitTest(_root.game["p" + _parent.pn].mc.zh2atm) || hitTest(_root.game["p" + _parent.pn].mc.zh3atm) || hitTest(_root.game["p" + _parent.pn].mc.abcd))
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
         _X = _X + movspeed;
         _Y = _Y + movspeed;
      }
   }
}
