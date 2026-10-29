onClipEvent(load){
   if(_parent._parent._xscale < 0)
   {
      if(_root.game["p" + _parent.pn]._x > _parent._parent._x)
      {
         return undefined;
      }
      _X = (- (_root.game["p" + _parent.pn]._x - _parent._parent._x)) / (_parent._xscale / 100);
   }
   else
   {
      if(_root.game["p" + _parent.pn]._x < _parent._parent._x)
      {
         return undefined;
      }
      _X = (_root.game["p" + _parent.pn]._x - _parent._parent._x) / (_parent._xscale / 100);
   }
}
