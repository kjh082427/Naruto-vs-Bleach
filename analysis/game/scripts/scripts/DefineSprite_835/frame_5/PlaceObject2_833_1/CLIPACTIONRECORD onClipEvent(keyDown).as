onClipEvent(keyDown){
   _root[_parent._parent.key] = Key.getCode();
   trace(_parent._parent.key + "," + _root[_parent._parent.key]);
   _parent.gotoAndStop(1);
}
