function gameRunning()
{
   return _root.zhanting == false && _root.game["p" + _parent.pn].mc.sw == false;
}
function beida()
{
   var _loc2_ = checkHit();
   if(!_loc2_)
   {
      return undefined;
   }
   _parent.jhp = _loc2_.pw;
   _parent.bdzl = _loc2_.zl;
   _parent.yup = _loc2_.yup;
   _parent.htx = _loc2_.hitx;
   _parent.time = 0;
   _parent.tdtime = _loc2_.hdtime / 1000 * 30;
   if(isNaN(_parent.tdtime))
   {
      _parent.tdtime = 0;
   }
   if(_parent.bdzl > 10)
   {
      _parent.bdzl -= 10;
   }
   _parent.gotoAndPlay(_loc2_.htype);
}
function fangyu()
{
   var _loc2_ = checkHit();
   if(!_loc2_)
   {
      return undefined;
   }
   _parent.jhp = _loc2_.pw;
   _parent.htx = _loc2_.hitx;
   _parent.yup = _loc2_.yup;
   _parent.bdzl = _loc2_.zl;
   _parent.tdtime = _loc2_.hdtime / 1000 * 30;
   if(isNaN(_parent.tdtime))
   {
      _parent.tdtime = 0;
   }
   if(_parent.bdzl > 10)
   {
      _parent.bdzl -= 10;
      _parent.gotoAndPlay(_loc2_.htype);
   }
   else
   {
      _parent.yup = 0;
      _parent.gotoAndPlay("防住");
   }
}
function checkHit()
{
   if(!gameRunning())
   {
      return null;
   }
   if(!_parent.canhit)
   {
      return null;
   }
   var _loc3_ = getHitObj(_fsArray,_root.game["p" + _parent.pn].mc,"atm",_parent.pw);
   if(!_loc3_)
   {
      _loc3_ = getHitObj(_fzfsArray,_root.game["p" + _parent.pn + "fz"],"",_parent.fzpw);
   }
   if(!_loc3_)
   {
      _loc3_ = getStgHitObj();
   }
   return _loc3_;
}
function getHitObj(array, player, afterFix, ppw)
{
   if(afterFix == undefined)
   {
      afterFix = "";
   }
   var _loc2_;
   var _loc4_;
   for(var _loc13_ in array)
   {
      _loc2_ = array[_loc13_];
      _loc4_ = player[_loc2_ + afterFix];
      if(_loc4_)
      {
         if(this.hitTest(_loc4_))
         {
            return {pw:ppw[_loc2_ + "pw"],zl:ppw[_loc2_ + "zl"],yup:ppw[_loc2_ + "up"],hitx:ppw[_loc2_ + "x"],hdtime:ppw[_loc2_ + "tm"],htype:ppw[_loc2_ + "dz"]};
         }
      }
   }
   return null;
}
function getStgHitObj()
{
   var _loc4_;
   for(var _loc5_ in stgks)
   {
      _loc4_ = _root.game.layer_effect[stgks[_loc5_] + "_P" + _parent.pn];
      if(_loc4_)
      {
         if(this.hitTest(_loc4_.mian))
         {
            return _loc4_.hitObj;
         }
      }
   }
}
var hitks = ["tk","tz","k1","k2","k3","k4","k5","kj1","kj2","zh1","zh2","zh3","bs","sbs","cbs","kbs"];
var stgks = ["stgk1","stgk2","stgk3","stgk4","stgk5","stgk6","stgk7","stgk8","stgk9","stgk10"];
var _fsArray = [];
var i = 0;
while(i < hitks.length)
{
   var kv = hitks[i];
   _fsArray.push(kv);
   var k = 1;
   while(k <= 5)
   {
      _fsArray.push(kv + k);
      k++;
   }
   i++;
}
var _fzfsArray = ["atm1","atm2","atm3","atm4","atm5"];
