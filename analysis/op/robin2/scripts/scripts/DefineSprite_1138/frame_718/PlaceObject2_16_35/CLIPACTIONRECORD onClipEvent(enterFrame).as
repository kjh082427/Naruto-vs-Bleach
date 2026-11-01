onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         _parent.updateDirect();
         if(_parent.touchFloor)
         {
            _parent.gotoAndPlay("招30");
         }
         if(moveLeft())
         {
            _parent._parent._x -= 10;
         }
         if(moveRight())
         {
            _parent._parent._x += 10;
         }
         if(_parent.kis(_parent.上))
         {
            _parent._parent._y -= 5;
         }
         if(_parent.kis(_parent.下))
         {
            _parent._parent._y += 10;
         }
         if(jump())
         {
            _parent.gotoAndPlay("招30");
         }
         if(magichit3())
         {
            _parent.gotoAndPlay("招33");
         }
         if(magichit2())
         {
            _parent.gotoAndPlay("招34");
         }
         if(magichit1())
         {
            _parent.gotoAndPlay("招32");
         }
         if(nornalhit())
         {
            _parent.gotoAndPlay("招35");
         }
      }
   }
}
