onClipEvent(enterFrame){
   if(_root.zhanting == false)
   {
      _root.game["p" + _parent.pn]._visible = false;
      _root.game["p" + _parent.pn]._y -= 3;
   }
}
