onClipEvent(enterFrame){
   if(this.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      _parent.gotoAndPlay("攻击2");
   }
}
