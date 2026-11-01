onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.cbs0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("超必杀1");
         return undefined;
      }
      moveX(20);
   }
}
