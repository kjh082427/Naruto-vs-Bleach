if(_parent._xscale > 0)
{
   _parent._xscale = -100;
   _parent._x = _root.game["p" + pn]._x + 150;
}
else
{
   _parent._xscale = 100;
   _parent._x = _root.game["p" + pn]._x - 150;
}
updateDirect();
