onClipEvent(enterFrame){
   if(_parent.cselect == 4)
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
      _root.maxtime = 30;
   }
   if(cl == 2)
   {
      _root.maxtime = 60;
   }
   if(cl == 3)
   {
      _root.maxtime = 90;
   }
   if(cl == 4)
   {
      _root.maxtime = 100;
   }
}
