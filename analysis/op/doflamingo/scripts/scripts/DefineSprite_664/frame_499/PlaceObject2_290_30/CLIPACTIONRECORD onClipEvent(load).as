onClipEvent(load){
   if(Math.abs(_parent._parent._x - _root.game["p" + _parent.pn]._x) > 200)
   {
      return undefined;
   }
   if(_parent._parent._xscale > 0)
   {
      if(_parent._parent._x < _root.game["p" + _parent.pn]._x)
      {
         _X = _root.game["p" + _parent.pn]._x - _parent._parent._x;
      }
   }
   else if(_parent._parent._x > _root.game["p" + _parent.pn]._x)
   {
      _X = _parent._parent._x - _root.game["p" + _parent.pn]._x;
   }
}
