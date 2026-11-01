var _px = _parent._x;
var _tx = _root.game["p" + pn]._x;
if(_parent._xscale > 0 && _px > _tx)
{
   _parent._xscale *= -1;
}
if(_parent._xscale < 0 && _px < _tx)
{
   _parent._xscale *= -1;
}
updateDirect();
