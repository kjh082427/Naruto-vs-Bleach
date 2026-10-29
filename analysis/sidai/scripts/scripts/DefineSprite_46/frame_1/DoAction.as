beidax = function()
{
   if(_root.zhanting == false)
   {
      jx = _parent.htx * _root.game._xscale / 100;
      if(_parent._xscale > 0)
      {
         _parent._x -= jx;
      }
      else
      {
         _parent._x += jx;
      }
      _parent._y -= _parent.yup;
   }
};
fangyux = function()
{
   if(_root.zhanting == false)
   {
      fjx = Math.round(_parent.htx * _root.game._xscale / 100);
      if(_parent._xscale > 0)
      {
         _parent._x -= fjx;
      }
      else
      {
         _parent._x += fjx;
      }
   }
};
