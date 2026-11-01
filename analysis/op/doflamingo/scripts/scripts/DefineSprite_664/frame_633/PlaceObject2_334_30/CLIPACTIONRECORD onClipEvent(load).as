onClipEvent(load){
   if(_parent._parent._y - _root.game["p" + _parent.pn]._y < 30)
   {
      return undefined;
   }
   if(_parent._parent._xscale > 0)
   {
      if(_root.game["p" + _parent.pn]._x - _parent._parent._x > 250 || _parent._parent._x - _root.game["p" + _parent.pn]._x > 50)
      {
         return undefined;
      }
      _X = _root.game["p" + _parent.pn]._x - _parent._parent._x;
   }
   else
   {
      if(_parent._parent._x - _root.game["p" + _parent.pn]._x > 250 || _root.game["p" + _parent.pn]._x - _parent._parent._x > 50)
      {
         return undefined;
      }
      _X = _parent._parent._x - _root.game["p" + _parent.pn]._x;
   }
   _Y = _root.game["p" + _parent.pn]._y - _parent._parent._y;
}
