_root.cbsw(pn);
if(_parent._xscale > 0)
{
   bsatm._x = _root.game["p" + pn]._x - _parent._x;
}
else
{
   bsatm._x = _parent._x - _root.game["p" + pn]._x;
}
bsatm._y = _root.game["p" + pn]._y - _parent._y;
