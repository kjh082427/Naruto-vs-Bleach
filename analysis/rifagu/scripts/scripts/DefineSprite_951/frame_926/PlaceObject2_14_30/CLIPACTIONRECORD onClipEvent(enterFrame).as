onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      moveY(-25);
      if(_parent._parent._y > _root.game["p" + _parent.pn]._y - 10)
      {
         if(_parent.touchFloor)
         {
            _parent.gotoAndPlay("超必杀1");
         }
      }
   }
}
