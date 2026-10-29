onClipEvent(enterFrame){
   if(gameRunning())
   {
      var pp = _root.game["p" + _parent.pn];
      var self = _parent._parent;
      var xd = pp._x - self._x;
      if(Math.abs(xd) > 25)
      {
         pp._x += xd >= 0 ? -20 : 20;
      }
      var yd = pp._y - (self._y - 100);
      if(Math.abs(yd) > 25)
      {
         pp._y += yd >= 0 ? -20 : 20;
      }
   }
}
