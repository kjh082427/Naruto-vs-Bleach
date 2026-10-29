onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent._parent._xscale > 0)
      {
         if(_parent.bs10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
         {
            _parent.gotoAndPlay("超必杀1");
         }
         else
         {
            _parent._parent._x += Math.round(_parent.speed * 7);
         }
      }
      else if(_parent.bs10atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("超必杀1");
      }
      else
      {
         _parent._parent._x -= Math.round(_parent.speed * 7);
      }
   }
}
