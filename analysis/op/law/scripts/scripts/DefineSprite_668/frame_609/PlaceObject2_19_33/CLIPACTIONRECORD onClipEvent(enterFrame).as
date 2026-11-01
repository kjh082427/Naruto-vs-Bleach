onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(Math.abs(_parent._parent._x - _root.game["p" + _parent.pn]._x) < 80)
      {
         _parent.gotoAndPlay("招12");
         return undefined;
      }
      moveX(_parent.speed * 3);
      _parent._parent.showdow({R:-67,G:-169,B:-255});
   }
}
