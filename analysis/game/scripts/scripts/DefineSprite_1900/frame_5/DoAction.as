var po1 = _root.getFighterData(_root.p1selt);
var po2 = _root.getFighterData(_root.p2selt);
var p1frame = po1.WKframe;
var p2frame = po2.WKframe;
if(!isNaN(p1frame) && p1frame > 1)
{
   _root.game.p1.gotoAndStop(p1frame);
}
if(!isNaN(p2frame) && p2frame > 1)
{
   _root.game.p2.gotoAndStop(p2frame);
}
_root.game.p1.initCtrl(_root.p1cpu);
_root.game.p2.initCtrl(_root.p2cpu);
