function lf()
{
   if(_root.loadingFunc == undefined)
   {
      return true;
   }
   return _root.loadingFunc();
}
_root.loadingGame = true;
