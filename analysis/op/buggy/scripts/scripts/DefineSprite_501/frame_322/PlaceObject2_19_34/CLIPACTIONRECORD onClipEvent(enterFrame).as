onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(skill2())
         {
            _parent.gotoAndPlay("砍技21");
         }
         if(jump())
         {
            _parent.gotoAndPlay("跳");
         }
      }
   }
}
