if(_parent._xscale > 0)
{
   kj2atm._x = _root.game["p" + pn]._x - _parent._x;
}
else
{
   kj2atm._x = _parent._x - _root.game["p" + pn]._x;
}
kj2aDtm._y = _root.game["p" + pn]._y - _parent._y;
ql += 4;
