onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale > 0)
      {
         _parent._parent._x += Math.round(_parent.speed);
      }
      else
      {
         _parent._parent._x -= Math.round(_parent.speed);
      }
   }
   _parent._parent._y -= 15;
}
