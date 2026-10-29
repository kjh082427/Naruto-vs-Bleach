onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale > 0)
      {
         _parent._parent._x += Math.round(_parent.speed * 2);
      }
      else
      {
         _parent._parent._x -= Math.round(_parent.speed * 2);
      }
   }
}
