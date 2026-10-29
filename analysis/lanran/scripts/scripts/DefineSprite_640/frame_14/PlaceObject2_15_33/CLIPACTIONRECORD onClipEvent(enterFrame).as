onClipEvent(enterFrame){
   if(gameRunning())
   {
      if(defence())
      {
         _parent.gotoAndPlay("防御w");
      }
      if(nornalhit())
      {
         _parent.gotoAndPlay("跳砍");
      }
      if(wankai())
      {
         _parent.gotoAndPlay("万解");
      }
      if(skill2())
      {
         _parent.gotoAndPlay("砍技2w");
      }
      if(skill1())
      {
         _parent.gotoAndPlay("砍技1w");
      }
      if(magichit3())
      {
         _parent.gotoAndPlay("招3w");
      }
      if(magichit2())
      {
         _parent.gotoAndPlay("招2");
      }
      if(magichit1())
      {
         _parent.gotoAndPlay("招1");
      }
      if(bishaUP())
      {
         _parent.gotoAndPlay("上必杀");
      }
      if(bisha())
      {
         _parent.gotoAndPlay("必杀");
      }
      if(zhaoHuan())
      {
         _parent.gotoAndPlay("招换");
      }
      var ml = moveLeft();
      var mr = moveRight();
      if(ml)
      {
         _parent._parent._xscale = -100;
         _parent._parent.scale_X = -1;
      }
      if(mr)
      {
         _parent._parent._xscale = 100;
         _parent._parent.scale_X = 1;
      }
      if(rush())
      {
         _parent.gotoAndPlay("瞬步");
      }
      if(jump())
      {
         _parent.gotoAndPlay("跳2");
      }
      if(ml)
      {
         _parent._parent._x -= _parent.speed;
         _parent.gotoAndPlay("走1");
      }
      if(mr)
      {
         _parent._parent._x += _parent.speed;
         _parent.gotoAndPlay("走1");
      }
      if(!ml && !mr)
      {
         _parent.updateDirect();
      }
   }
}
