onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.kj10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("砍技11");
         return undefined;
      }
      moveX(_parent.speed * 3);
   }
}
