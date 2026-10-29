onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(_parent._parent._xscale > 0)
         {
            if(_parent.kj10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
            {
               _parent.gotoAndPlay("砍技12");
            }
            else
            {
               _parent._parent._x += Math.round(_parent.speed * 1.4);
            }
         }
         else if(_parent.kj10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
         {
            _parent.gotoAndPlay("砍技12");
         }
         else
         {
            _parent._parent._x -= Math.round(_parent.speed * 1.4);
         }
      }
   }
}
