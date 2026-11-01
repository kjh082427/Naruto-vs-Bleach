function goNext()
{
   Key.removeListener(keyListener);
   gotoAndStop("in");
   play();
}
stop();
btn.onRelease = goNext;
var keyListener = new Object();
keyListener.onKeyDown = goNext;
Key.addListener(keyListener);
