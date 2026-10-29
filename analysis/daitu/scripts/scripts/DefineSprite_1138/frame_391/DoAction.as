if(_parent._x < _root.game["p" + pn]._x)
{
   _parent._xscale *= -1;
}
if(_parent._xscale < 0)
{
   if(_parent._x < _root.game["p" + pn]._x)
   {
      _parent._xscale *= -1;
   }
}
else if(_parent._x > _root.game["p" + pn]._x)
{
   _parent._xscale *= -1;
}
