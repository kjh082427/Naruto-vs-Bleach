onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      if(_root.game["p" + _parent.pn].mc.sw == false)
      {
         if(_parent._parent._xscale < 0)
         {
            _parent._parent._x -= _parent.speed * 2.5;
         }
         else
         {
            _parent._parent._x += _parent.speed * 2.5;
         }
         if(bishaUP())
         {
            _parent.gotoAndPlay("上必杀");
         }
         if(bishaSuper())
         {
            _parent.gotoAndPlay("超必杀");
         }
         if(_parent.ql >= 100)
         {
            if(_parent.kis(_parent.必杀))
            {
               _parent.gotoAndPlay("必杀");
            }
         }
      }
   }
}
