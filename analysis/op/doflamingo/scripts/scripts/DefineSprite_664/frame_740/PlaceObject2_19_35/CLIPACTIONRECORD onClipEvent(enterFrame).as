onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.zh20atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("招22");
         return undefined;
      }
      moveX(_parent.speed * 6);
      _parent._parent.showdow({R:255,G:255,B:255});
   }
}
