onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.zh10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn) || _parent.zh10atm.hitTest(_root.game["p" + _parent.pn].mc.jiao))
      {
         _parent._parent._xscale *= -1;
         _parent.gotoAndPlay("招12");
      }
      else
      {
         moveX(_parent.speed * 2);
      }
   }
}
