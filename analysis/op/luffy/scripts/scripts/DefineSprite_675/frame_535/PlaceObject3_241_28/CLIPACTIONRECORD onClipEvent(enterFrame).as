onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(mian.hitTest(_root.game["p" + _parent.pn].mc.bdmn) or mian.hitTest(_root.game["p" + _parent.pn].mc.zh1atm) or mian.hitTest(_root.game["p" + _parent.pn].mc.zh2atm) or mian.hitTest(_root.game["p" + _parent.pn].mc.zh3atm) or mian.hitTest(_root.game["p" + _parent.pn].mc.abcd))
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
      }
   }
}
