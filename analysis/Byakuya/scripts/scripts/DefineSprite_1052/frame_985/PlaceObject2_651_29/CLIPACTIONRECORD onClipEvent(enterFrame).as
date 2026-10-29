onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false && _parent.sw == false)
      {
         if(_parent.kis(_parent.冲))
         {
            _parent.gotoAndPlay("起身");
         }
      }
   }
}
