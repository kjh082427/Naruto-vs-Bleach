onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.tz0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("跳招3");
         return undefined;
      }
      moveY(-20);
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招2");
      }
      _parent._parent.showdow({R:200,B:200});
   }
}
