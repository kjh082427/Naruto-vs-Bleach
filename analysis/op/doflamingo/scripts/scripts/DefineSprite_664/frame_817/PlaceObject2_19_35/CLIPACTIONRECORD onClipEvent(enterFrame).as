onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.zh30atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("招32");
         return undefined;
      }
      moveX(_parent.speed * 1.5);
      moveY(_parent.speed * 1.5);
      _parent._parent.showdow({R:255,G:255,B:255});
   }
}
