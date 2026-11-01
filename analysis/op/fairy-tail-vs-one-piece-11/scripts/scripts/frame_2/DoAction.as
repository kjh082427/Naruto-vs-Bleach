function menu_menu(obj, item)
{
   if(isload)
   {
      _root.gotoAndStop("MENU");
   }
}
function menu_pass(obj, item)
{
   if(isload)
   {
      _root.gotoAndStop("YOUWIN");
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
   fullScreen(!fullscreen_mode);
}
function fullScreen(v)
{
   fullscreen_mode = v;
   if(v)
   {
      fscommand("fullscreen","false");
   }
   else
   {
      fscommand("fullscreen","true");
   }
}
stop();
System.useCodepage = false;
if(adType == NO_AD)
{
   fullScreen(true);
}
var isload = false;
var showNews = true;
myMenu = new ContextMenu();
myMenu.hideBuiltInItems();
myMenu.customItems.push(new ContextMenuItem("Menu - 标题画面",menu_menu));
if(_root.debug)
{
   myMenu.customItems.push(new ContextMenuItem("Reset",menu_reset));
   myMenu.customItems.push(new ContextMenuItem("Pass",menu_pass));
}
myMenu.customItems.push(new ContextMenuItem("MoreGames - 更多游戏",menu_more));
myMenu.customItems.push(new ContextMenuItem("5dplay.net - 出品网站",menu_website));
myMenu.customItems.push(new ContextMenuItem("DownGame - 下载本游戏",menu_down));
myMenu.customItems.push(new ContextMenuItem("FullScreen - 全屏游戏",menu_full));
var fullscreen_mode = false;
if(adType == TYPE_4399)
{
   Stage.showMenu = false;
}
else
{
   _root.menu = myMenu;
}
