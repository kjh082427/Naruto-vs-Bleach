onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _parent._parent._y -= Math.round(_parent.speed * 0.5);
      if(_parent._parent._xscale > 0)
      {
         _parent._parent._x += Math.round(_parent.speed * 0.5);
      }
      else
      {
         _parent._parent._x -= Math.round(_parent.speed * 0.5);
      }
   }
}
