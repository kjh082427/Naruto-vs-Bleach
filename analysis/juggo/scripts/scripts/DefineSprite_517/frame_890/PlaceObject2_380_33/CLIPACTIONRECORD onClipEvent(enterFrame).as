onClipEvent(enterFrame){
   var pp = _root.game["p" + _parent.pn];
   var self = _parent._parent;
   if(_root.zhanting == false && pp.mc.sw == false)
   {
      pp._x = self._x + _X * (self._xscale / 100);
      pp._y = self._y + _Y;
   }
}
