onClipEvent(enterFrame){
   if(_root.game["p" + _parent.pn].mc.sw == false)
   {
      if(defence())
      {
         _parent.gotoAndPlay("防御ww");
      }
   }
}
