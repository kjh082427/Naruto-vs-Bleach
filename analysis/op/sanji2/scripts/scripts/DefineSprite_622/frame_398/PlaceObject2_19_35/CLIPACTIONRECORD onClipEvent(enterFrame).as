onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.zh10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("招11");
      }
      else
      {
         moveX(_parent.speed * 2);
         _parent._parent.showdow({R:255});
      }
   }
}
