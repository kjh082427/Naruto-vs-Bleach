if(_parent._xscale > 0)
{
   dogs._x = _root.game["p" + pn]._x - _parent._x;
}
else
{
   dogs._x = _parent._x - _root.game["p" + pn]._x;
}
dogs._y = _root.game["p" + pn]._y - _parent._y;
