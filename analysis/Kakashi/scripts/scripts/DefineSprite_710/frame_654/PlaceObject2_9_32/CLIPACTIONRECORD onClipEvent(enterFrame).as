onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(_parent.kis(_parent.斩))
         {
            _parent.gotoAndPlay("跳砍");
         }
      }
   }
}
