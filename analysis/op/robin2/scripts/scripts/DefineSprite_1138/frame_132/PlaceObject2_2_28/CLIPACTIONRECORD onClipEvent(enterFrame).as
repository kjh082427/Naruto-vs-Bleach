onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("跳砍2");
      }
   }
}
