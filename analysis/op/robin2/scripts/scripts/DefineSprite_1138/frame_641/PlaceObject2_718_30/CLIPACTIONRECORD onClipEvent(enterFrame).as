onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._flowerHit == 0)
      {
         if(hitTest(_root.game["p" + _parent.pn].mc.bdmn) or hitTest(_root.game["p" + _parent.pn].mc.zh1atm) or hitTest(_root.game["p" + _parent.pn].mc.zh2atm) or hitTest(_root.game["p" + _parent.pn].mc.zh3atm) or hitTest(_root.game["p" + _parent.pn].mc.abcd))
         {
            _parent._flowerHit = 1;
            if(_parent.zzz._currentframe == 1)
            {
               _parent.zzz.gotoAndPlay(2);
            }
         }
      }
      else if(_parent.zzz._currentframe == 1)
      {
         _parent.zzz.gotoAndPlay(2);
      }
   }
}
