if(_parent._xscale > 0)
{
   _parent._x = _root.game["p" + pn]._x + _root.game["p" + pn].mc.bdmn._width + 100;
}
else
{
   _parent._x = _root.game["p" + pn]._x - _root.game["p" + pn].mc.bdmn._width - 100;
}
_root.shine();
