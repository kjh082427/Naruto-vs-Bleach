onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.tz0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("跳招3");
         return undefined;
      }
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("跳招4");
         return undefined;
      }
      if(_parent._parent._xscale < 0)
      {
         _parent._parent._x -= 10;
      }
      else
      {
         _parent._parent._x += 10;
      }
      _parent._parent._y += 10;
   }
}
