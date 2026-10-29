onClipEvent(enterFrame){
   if(_parent.cselect == 2)
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
      _root.AI = 5;
   }
   if(cl == 2)
   {
      _root.AI = 4;
   }
   if(cl == 3)
   {
      _root.AI = 3;
   }
   if(cl == 4)
   {
      _root.AI = 2;
   }
   if(cl == 5)
   {
      _root.AI = 1;
   }
}
