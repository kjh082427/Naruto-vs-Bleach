if(_parent._xscale > 0)
{
   _parent._xscale = -100;
   _parent._x = _root.game["p" + pn]._x - _root.game["p" + pn].mc.bdmn._width * 0.7;
}
else
{
   _parent._xscale = 100;
   _parent._x = _root.game["p" + pn]._x + _root.game["p" + pn].mc.bdmn._width * 0.7;
}
_parent._y = _root.game["p" + pn]._y + _root.game["p" + pn].mc.bdmn._height * 0.5;
_root.shine();
