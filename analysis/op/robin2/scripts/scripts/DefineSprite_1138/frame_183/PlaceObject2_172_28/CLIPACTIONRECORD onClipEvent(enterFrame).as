onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(played == 0)
      {
         if(hitTest(_root.game["p" + _parent.pn].mc.bdmn))
         {
            played = 1;
            _parent.gotoAndPlay("跳招1");
         }
         _X = _X + 5;
         _Y = _Y + 5;
      }
   }
}
