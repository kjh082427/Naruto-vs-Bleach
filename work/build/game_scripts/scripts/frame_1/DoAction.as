function showCommt()
{
   if(allowGoLink)
   {
      goLink();
      return undefined;
   }
   if(_global.bridge)
   {
      _global.bridge.showGameList();
   }
}
function goLink(url)
{
}
_root.ver = "V 1.3";
_root.date_ver = "2016/6/23";
var adType;
var wudi = false;
var TYPE_4399 = "4399";
var allowGoLink = true;
var NO_AD = "no-ad";
var debuging = true;
adType = TYPE_4399;
var _loc0_;
if((_loc0_ = adType) === TYPE_4399)
{
   _global.bridge = AS2_4399_API.Bridge.getInstance();
   var _4399_function_ad_id = "944c23f5e64a80647f8d0f3435f5c7a8";
   allowGoLink = false;
}
