stop();
_root.gametime = _root.maxtime;
time = function()
{
   if(_root.zhanting == false)
   {
      if(_root.game.p1.mc.sw == false and _root.game.p2.mc.sw == false)
      {
         if(_root.modo != 4)
         {
            _root.gametime -= 1;
         }
      }
   }
   tm = _root.gametime;
   if(tm <= 0)
   {
      if(_root.timeover.played == 0)
      {
         _root.to = true;
         _root.timeover.play();
         played = 1;
      }
      tm = 0;
   }
   else
   {
      _root.to = false;
   }
   if(tm >= 10)
   {
      shi = Math.floor(tm / 10);
      gs = tm - shi * 10;
   }
   if(tm < 10)
   {
      shi = 0;
      gs = tm;
   }
   十.gotoAndStop(shi + 1);
   个.gotoAndStop(gs + 1);
};
if(_root.maxtime == 100 or _root.modo == 4)
{
   gotoAndStop("无限时");
}
else
{
   gotoAndPlay(2);
}
