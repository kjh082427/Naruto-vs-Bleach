onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(_parent._parent._xscale < 0)
         {
            if(_parent.zh10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
            {
               _parent._parent._xscale = 100;
               _parent.gotoAndPlay("招12");
            }
            else
            {
               _parent._parent._x -= _parent.speed * 2;
            }
         }
         else if(_parent.zh10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
         {
            _parent._parent._xscale = -100;
            _parent.gotoAndPlay("招12");
         }
         else
         {
            _parent._parent._x += _parent.speed * 2;
         }
      }
   }
}
