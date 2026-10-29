onClipEvent(load){
   if(_parent._parent._xscale < 0)
   {
      _X = - (_root.game["p" + _parent.pn]._x - _parent._parent._x);
   }
   else
   {
      _X = _root.game["p" + _parent.pn]._x - _parent._parent._x;
   }
}
