onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(skill1())
         {
            _parent.gotoAndPlay("砍技1");
         }
         if(magichit3())
         {
            _parent.gotoAndPlay("招3");
         }
         if(magichit2())
         {
            _parent.gotoAndPlay("招2");
         }
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
      }
   }
}
