onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(_parent._parent._xscale < 0)
         {
            if(_parent.bs0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
            {
               _parent.gotoAndPlay("必杀2");
            }
            else
            {
               _parent._parent._x -= _parent.speed * 2;
            }
         }
         else if(_parent.bs0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
         {
            _parent.gotoAndPlay("必杀2");
         }
         else
         {
            _parent._parent._x += _parent.speed * 2;
         }
      }
   }
}
