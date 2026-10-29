if(_parent._xscale < 0)
{
   _parent._xscale = 100;
   _parent._x = _root.game["p" + pn]._x - 40;
}
else
{
   _parent._xscale = -100;
   _parent._x = _root.game["p" + pn]._x + 40;
}
_parent._y = _root.game["p" + pn]._y - 40;
_root.shine();
