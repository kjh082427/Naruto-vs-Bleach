onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         var xpd = 25;
         var jl = 10;
         if(_parent._parent._xscale < 0)
         {
            if(_parent._parent._x - _root.game["p" + _parent.pn]._x < - jl)
            {
               _parent.setDirect(1);
               _parent.gotoAndPlay("砍技22");
            }
            else
            {
               _parent._parent._x -= xpd;
            }
         }
         else if(_parent._parent._x - _root.game["p" + _parent.pn]._x > jl)
         {
            _parent.setDirect(-1);
            _parent.gotoAndPlay("砍技22");
         }
         else
         {
            _parent._parent._x += xpd;
         }
      }
   }
}
