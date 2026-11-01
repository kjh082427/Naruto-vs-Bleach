onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(bisha())
         {
            _parent.gotoAndPlay("必杀");
         }
         if(skill2())
         {
            _parent.gotoAndPlay("砍技22");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招12");
         }
         if(dohide())
         {
            _parent.gotoAndPlay("起身");
         }
      }
   }
}
