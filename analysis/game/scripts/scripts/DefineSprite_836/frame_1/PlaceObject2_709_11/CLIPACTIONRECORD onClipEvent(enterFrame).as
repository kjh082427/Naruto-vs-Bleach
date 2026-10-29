onClipEvent(enterFrame){
   if(_parent.cselect == 5)
   {
      left._visible = true;
      right._visible = true;
   }
   else
   {
      left._visible = false;
      right._visible = false;
   }
   this.gotoAndStop(cl);
   if(cl == 1)
   {
      _root.maxhp = 1000;
   }
   if(cl == 2)
   {
      _root.maxhp = 2000;
   }
   if(cl == 3)
   {
      _root.maxhp = 3000;
   }
   if(cl == 4)
   {
      _root.maxhp = 4000;
   }
   if(cl == 5)
   {
      _root.maxhp = 5000;
   }
}
