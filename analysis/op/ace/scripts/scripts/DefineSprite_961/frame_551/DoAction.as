if(_parent._xscale > 0)
{
   if(_parent._x < _root.game["p" + pn]._x)
   {
      zzz._x = _root.game["p" + pn]._x - _parent._x;
   }
}
else if(_parent._x > _root.game["p" + pn]._x)
{
   zzz._x = _parent._x - _root.game["p" + pn]._x;
}
