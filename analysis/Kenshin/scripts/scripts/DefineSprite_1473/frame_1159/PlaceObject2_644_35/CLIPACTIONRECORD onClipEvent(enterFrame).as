onClipEvent(enterFrame){
   if(this.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         _root.game["p" + _parent.pn].mc.gotoAndPlay("被打");
      }
   }
}
