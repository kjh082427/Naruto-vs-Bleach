onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_parent.touch == true)
      {
         _parent.gotoAndPlay("上必杀3");
         return undefined;
      }
      if(_parent.sbs0atm.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
      {
         _parent.gotoAndPlay("上必杀2");
      }
      else
      {
         moveX(10);
         moveY(-15);
         _parent._parent.showdow({R:255});
      }
   }
}
