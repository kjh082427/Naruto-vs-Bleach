function show()
{
   if(_root.readying)
   {
      return undefined;
   }
   _root.zhanting = true;
   trace("zhanting" + _root.zhanting);
   skk._y = ky[kn];
   _visible = true;
   gotoAndStop(1);
}
stop();
btn0.onRelease = function()
{
   Key.removeListener(keyListener);
   _root.gotoAndStop("MENU");
};
btn1.onRelease = function()
{
   play();
};
btn2.onRelease = function()
{
   _root.zhanting = false;
   _visible = false;
};
kn = 2;
var an = 0;
var anx = 5;
onEnterFrame = function()
{
   if(_root.readying)
   {
      return undefined;
   }
   if(_currentframe != 1)
   {
      return undefined;
   }
   if(an > 0)
   {
      an--;
      return undefined;
   }
   if(Key.isDown(13))
   {
      an = anx;
      trace("DOWN_ENTER" + _visible);
      if(_visible == false)
      {
         show();
      }
      else
      {
         if(kn == 0)
         {
            Key.removeListener(keyListener);
            _root.gotoAndStop("MENU");
         }
         if(kn == 1)
         {
            play();
         }
         if(kn == 2)
         {
            _root.zhanting = false;
            _visible = false;
         }
      }
   }
   if(_visible == true)
   {
      if(Key.isDown(40))
      {
         an = anx;
         if(kn < ky.length - 1)
         {
            kn += 1;
         }
         else
         {
            kn = 0;
         }
         skk._y = ky[kn];
      }
      if(Key.isDown(38))
      {
         an = anx;
         if(kn > 0)
         {
            kn -= 1;
         }
         else
         {
            kn = ky.length - 1;
         }
         skk._y = ky[kn];
      }
   }
};
