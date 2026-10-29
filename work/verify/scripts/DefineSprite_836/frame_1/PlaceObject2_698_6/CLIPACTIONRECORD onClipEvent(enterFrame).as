onClipEvent(enterFrame){
   if(_parent.cselect == 3)
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
      _root._quality = "HIGH";
   }
   if(cl == 2)
   {
      _root._quality = "MEDIUM";
   }
   if(cl == 3)
   {
      _root.quality = "LOW";
   }
}
