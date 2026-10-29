function menu_menu(obj, item)
{
   if(isload)
   {
      _root.gotoAndStop("MENU");
   }
}
function menu_reset(obj, item)
{
   _root.gotoAndPlay(55);
}
function menu_more(obj, item)
{
   _root.goLink();
}
function menu_website(obj, item)
{
   _root.goLink();
}
function menu_down(obj, item)
{
   _root.goLink("downbvn.html");
}
function menu_full(obj, item)
{
   if(Stage.displayState == "fullScreen")
   {
      Stage.displayState = "normal";
      Stage.scaleMode = "showAll";
   }
   else
   {
      Stage.displayState = "fullScreen";
   }
}
stop();
System.useCodepage = false;
Stage.displayState = "fullScreen";
_root.cacheAsBitmap = true;
var isload = false;
var showNews = true;
myMenu = new ContextMenu();
myMenu.hideBuiltInItems();
myMenu.customItems.push(new ContextMenuItem("Menu - 标题画面",menu_menu));
if(debuging)
{
   myMenu.customItems.push(new ContextMenuItem("Reset",menu_reset));
}
myMenu.customItems.push(new ContextMenuItem("MoreGames - 更多游戏",menu_more));
myMenu.customItems.push(new ContextMenuItem("5dplay.net - 出品网站",menu_website));
myMenu.customItems.push(new ContextMenuItem("FullScreen - 全屏游戏",menu_full));
if(adType == TYPE_4399)
{
   Stage.showMenu = false;
}
else
{
   _root.menu = myMenu;
}
_root.scrollRect = new flash.geom.Rectangle(0,0,600,400);
