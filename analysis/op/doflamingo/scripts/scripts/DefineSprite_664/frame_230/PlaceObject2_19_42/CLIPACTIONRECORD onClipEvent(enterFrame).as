onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.tz0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("跳招2");
         return undefined;
      }
      moveX(_parent.speed * 3);
      _parent._parent.showdow({R:255,G:255,B:255});
      if(gameRunning())
      {
         if(bishaAir())
         {
            _parent.gotoAndPlay("空中必杀");
         }
         if(moveUp())
         {
            moveY(_parent.speed);
         }
         if(moveDown())
         {
            moveY(- _parent.speed);
         }
         if(jump())
         {
            _parent.gotoAndPlay("落2");
         }
      }
   }
}
