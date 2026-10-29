onClipEvent(enterFrame){
   if(gameRunning())
   {
      var pp = _root.game["p" + _parent.pn];
      var self = _parent._parent;
      var xd = pp._x - self._x;
      var yd = pp._y - self._y;
      var xin = true;
      var yin = true;
      if(Math.abs(xd) > 15)
      {
         pp._x += xd >= 0 ? -10 : 10;
         xin = false;
      }
      if(Math.abs(yd) > 15)
      {
         pp._y += yd >= 0 ? -10 : 10;
         yin = false;
      }
      if(xin && yin)
      {
         _parent.gotoAndPlay("上必杀2");
      }
   }
}
