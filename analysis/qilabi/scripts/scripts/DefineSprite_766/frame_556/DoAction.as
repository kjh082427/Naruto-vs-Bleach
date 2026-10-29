if(_parent._xscale < 0)
{
   _parent._xscale = 100;
   _parent.scale_X = 1;
   _parent._x = _root.game["p" + pn]._x - 80;
}
else
{
   _parent._xscale = -100;
   _parent.scale_X = -1;
   _parent._x = _root.game["p" + pn]._x + 80;
}
