onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.kj10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn) || _parent.kj10atm.hitTest(_root.game["p" + _parent.pn].mc.jiao))
      {
         _parent.gotoAndPlay("砍技12");
      }
      else
      {
         moveX(_parent.speed * 2);
      }
   }
}
