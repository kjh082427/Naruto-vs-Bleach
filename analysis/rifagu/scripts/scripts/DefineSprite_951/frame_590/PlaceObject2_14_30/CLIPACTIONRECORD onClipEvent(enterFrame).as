onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveX(35);
      if(_parent.bs0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("必杀1");
      }
   }
}
