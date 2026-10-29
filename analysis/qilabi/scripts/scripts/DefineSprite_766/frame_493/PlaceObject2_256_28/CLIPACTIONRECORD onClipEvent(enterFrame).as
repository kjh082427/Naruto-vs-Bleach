onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(main.hitTest(_root.game["p" + _parent.pn].mc.bdmn) or main.hitTest(_root.game["p" + _parent.pn].mc.zh1atm) or main.hitTest(_root.game["p" + _parent.pn].mc.zh2atm) or main.hitTest(_root.game["p" + _parent.pn].mc.zh3atm) or main.hitTest(_root.game["p" + _parent.pn].mc.abcd))
      {
         if(played == 0)
         {
            played = 1;
            movspeed = 0;
            gotoAndPlay(5);
         }
      }
      else if(played == 0)
      {
         _X = _X + 25;
         _Y = _Y - 15;
      }
   }
}
