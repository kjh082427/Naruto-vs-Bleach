onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.cbs0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn) || _parent.kj10atm.hitTest(_root.game["p" + _parent.pn].mc.jiao))
      {
         _parent.gotoAndPlay("超必杀2");
      }
      else
      {
         moveX(_parent.speed * 3);
      }
   }
}
