onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(_parent._parent._xscale > 0)
         {
            _parent._parent._x -= 2;
         }
         else
         {
            _parent._parent._x += 2;
         }
      }
      _parent._parent._y -= 2;
   }
}
