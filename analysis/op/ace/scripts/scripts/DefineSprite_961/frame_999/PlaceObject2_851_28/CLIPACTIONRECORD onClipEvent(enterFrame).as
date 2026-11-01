onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(played == 0)
      {
         if(mian.hitTest(_root.game["p" + _parent.pn].mc.bdmn) or mian.hitTest(_root.game["p" + _parent.pn].mc.zh1atm) or mian.hitTest(_root.game["p" + _parent.pn].mc.zh2atm) or mian.hitTest(_root.game["p" + _parent.pn].mc.zh3atm) or mian.hitTest(_root.game["p" + _parent.pn].mc.abcd))
         {
            played = 1;
            gotoAndPlay(5);
         }
         _X = _X + 20;
         _Y = _Y + 5;
      }
   }
}
