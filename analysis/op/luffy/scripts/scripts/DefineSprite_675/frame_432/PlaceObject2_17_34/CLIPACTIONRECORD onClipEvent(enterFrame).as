onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.kj20atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("砍技21");
         return undefined;
      }
      moveX(_parent.speed * 1.5);
      _parent._parent.showdow({R:255,G:-30});
   }
}
