onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.kj20atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("砍技21");
      }
      else if(_parent._parent._xscale > 0)
      {
         _parent._parent._x += _parent.speed * 3;
      }
      else
      {
         _parent._parent._x -= _parent.speed * 3;
      }
   }
}
