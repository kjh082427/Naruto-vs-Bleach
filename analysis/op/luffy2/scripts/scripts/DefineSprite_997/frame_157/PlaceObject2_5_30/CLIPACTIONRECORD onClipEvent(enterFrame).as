onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(this.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.kihit = true;
      }
   }
}
