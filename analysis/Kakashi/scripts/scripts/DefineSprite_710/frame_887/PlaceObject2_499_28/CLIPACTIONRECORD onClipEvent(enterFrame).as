onClipEvent(enterFrame){
   if(this.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      trace("hit:" + _parent.Cbshit);
      _parent.Cbshit = true;
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         _root.game["p" + _parent.pn].mc.gotoAndPlay("被打");
      }
   }
}
