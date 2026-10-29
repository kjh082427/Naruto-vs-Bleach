onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(_parent.zh20atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
         {
            _parent.gotoAndPlay("招22");
         }
      }
   }
}
