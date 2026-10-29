if(_parent._xscale > 0)
{
   kj2atm._x = _root.game["p" + pn]._x - _parent._x;
}
else
{
   kj2atm._x = _parent._x - _root.game["p" + pn]._x;
}
kj2atm._y = _root.game["p" + pn]._y - _parent._y;
