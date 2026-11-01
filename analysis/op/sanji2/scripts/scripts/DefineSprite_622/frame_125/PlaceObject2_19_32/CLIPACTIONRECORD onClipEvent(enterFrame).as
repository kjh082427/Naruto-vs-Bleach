onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.tk10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("跳砍1");
      }
      else
      {
         moveX(_parent.speed * 2);
         _parent._parent.showdow({B:255});
      }
   }
}
