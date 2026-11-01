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
   if(adType == TYPE_3366)
   {
      open3366.as2.Open3366Api.recomGame();
   }
}
function goLink(url)
{
}
_root.ver = "V 1.1";
_root.date_ver = "2016/7/25";
scrollRect = new flash.geom.Rectangle(0,0,600,400);
var wudi = false;
var debug = false;
var adType;
var TYPE_4399 = "4399";
var TYPE_3366 = "3366";
var allowGoLink = true;
var NO_AD = "no-ad";
adType = TYPE_4399;
switch(adType)
{
   case TYPE_4399:
      _global.bridge = AS2_4399_API.Bridge.getInstance();
      var _4399_function_gameList_id = "944c23f5e64a80647f8d0f3435f5c7a8";
      allowGoLink = false;
      break;
   case TYPE_3366:
      allowGoLink = false;
}
