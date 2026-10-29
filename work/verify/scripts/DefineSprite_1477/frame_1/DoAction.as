function init(type)
{
   isFighter = type == 0;
   isFZ = type == 1;
   isMap = type == 2;
   if(isMap)
   {
      updateXY(1,1,0);
      return undefined;
   }
   if(isFZ)
   {
      _root.p1sf = "";
      _root.p2sf = "";
   }
   else
   {
      _root.p1selt = "";
      _root.p2selt = "";
   }
   if(_root.modo == 3)
   {
      p2enable = true;
   }
   if(p1enable)
   {
      showP1();
   }
   if(p2enable)
   {
      showP2();
   }
}
function showP1()
{
   p1enable = true;
   var _loc1_ = 5;
   while(_loc1_ > 0)
   {
      if(updateXY(1,_loc1_,7))
      {
         break;
      }
      _loc1_ -= 1;
   }
}
function showP2()
{
   p2enable = true;
   var _loc1_ = 7;
   while(_loc1_ < 12)
   {
      if(updateXY(2,_loc1_,7))
      {
         break;
      }
      _loc1_ += 1;
   }
}
function alpha50()
{
   for(var _loc2_ in _grid)
   {
      for(var _loc1_ in _grid[_loc2_])
      {
         _grid[_loc2_][_loc1_]._alpha = 50;
      }
   }
   if(_p1selt)
   {
      _p1selt._alpha = 100;
   }
   if(_p2selt)
   {
      _p2selt._alpha = 100;
   }
}
function updateSelect(player)
{
   alpha50();
   var _loc5_ = _this["player" + player];
   var _loc2_ = _this["_p" + player + "selt"];
   var _loc4_ = _root["p" + player + "bst"];
   var _loc6_ = _root.getFighterData(_loc2_._name);
   if(isMap)
   {
      _root.curStage = _loc2_._name;
      _root.txt = _root.getMapData(_loc2_._name).name;
      _root.txtst = 0;
      return undefined;
   }
   if(isFighter)
   {
      _loc4_._visible = true;
      _loc4_.face.slt = _loc2_._name;
      _loc4_.gotoAndPlay(1);
   }
   _loc5_._visible = true;
   _loc5_._x = _loc2_._x;
   _loc5_._y = _loc2_._y;
   if(isFZ)
   {
      _root["p" + player + "sf"] = _loc2_._name;
   }
   else
   {
      _root["p" + player + "selt"] = _loc2_._name;
   }
   if(player == 1)
   {
      _root.txt = _loc6_.name;
      _root.txtst = 0;
   }
   else
   {
      _root.txt2 = _loc6_.name;
      _root.txtst2 = 0;
   }
}
function caozuo(player, l, r, u, d, ok, cl)
{
   if(_this["czint" + player] == undefined)
   {
      _this["czint" + player] = 10;
   }
   _this["czint" + player]++;
   if(_this["czint" + player] < 5)
   {
      return undefined;
   }
   var _loc3_ = _this["curx" + player];
   var _loc2_ = _this["cury" + player];
   if(Key.isDown(l))
   {
      _this["czint" + player] = 0;
      left(player);
      _root.keysound1.start();
   }
   if(Key.isDown(r))
   {
      _this["czint" + player] = 0;
      right(player);
      _root.keysound1.start();
   }
   if(Key.isDown(u))
   {
      _this["czint" + player] = 0;
      up(player);
      _root.keysound1.start();
   }
   if(Key.isDown(d))
   {
      _this["czint" + player] = 0;
      down(player);
      _root.keysound1.start();
   }
   if(Key.isDown(ok))
   {
      _this["czint" + player] = 0;
      _root.keysound2.start();
      _this["player" + player].gotoAndPlay(2);
      _this["p" + player + "enable"] = false;
      setTimeout(function()
      {
         onOK(player);
      }
      ,500);
   }
   if(Key.isDown(cl))
   {
      _this["czint" + player] = 0;
      _root.gotoAndStop("MENU");
   }
}
function left(player)
{
   var _loc2_ = _this["curx" + player];
   var _loc4_ = _this["cury" + player];
   if(_loc2_ <= xm)
   {
      _loc2_ = xx + 1;
   }
   var _loc3_ = false;
   var _loc1_ = _loc2_ - 1;
   while(_loc1_ >= xm)
   {
      if(updateXY(player,_loc1_,_loc4_))
      {
         _loc3_ = true;
         break;
      }
      _loc1_ -= 1;
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ - 1;
      while(_loc1_ >= xm)
      {
         if(updateXY(player,_loc1_,_loc4_ - 2))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ -= 1;
      }
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ - 1;
      while(_loc1_ >= xm)
      {
         if(updateXY(player,_loc1_,_loc4_ + 2))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ -= 1;
      }
   }
}
function right(player)
{
   var _loc2_ = _this["curx" + player];
   var _loc4_ = _this["cury" + player];
   if(_loc2_ >= xx)
   {
      _loc2_ = xm - 1;
   }
   var _loc3_ = false;
   var _loc1_ = _loc2_ + 1;
   while(_loc1_ <= xx)
   {
      if(updateXY(player,_loc1_,_loc4_))
      {
         _loc3_ = true;
         break;
      }
      _loc1_ += 1;
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ + 1;
      while(_loc1_ <= xx)
      {
         if(updateXY(player,_loc1_,_loc4_ - 2))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ += 1;
      }
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ + 1;
      while(_loc1_ <= xx)
      {
         if(updateXY(player,_loc1_,_loc4_ + 2))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ += 1;
      }
   }
}
function up(player)
{
   var _loc4_ = _this["curx" + player];
   var _loc2_ = _this["cury" + player];
   if(_loc2_ <= ym)
   {
      _loc2_ = yx + 1;
   }
   var _loc3_ = false;
   var _loc1_ = _loc2_ - 1;
   while(_loc1_ >= ym)
   {
      if(updateXY(player,_loc4_,_loc1_))
      {
         _loc3_ = true;
         break;
      }
      _loc1_ -= 1;
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ - 1;
      while(_loc1_ >= ym)
      {
         if(updateXY(player,_loc4_ - 2,_loc1_))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ -= 1;
      }
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ - 1;
      while(_loc1_ >= ym)
      {
         if(updateXY(player,_loc4_ + 2,_loc1_))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ -= 1;
      }
   }
}
function down(player)
{
   var _loc4_ = _this["curx" + player];
   var _loc2_ = _this["cury" + player];
   if(_loc2_ >= yx)
   {
      _loc2_ = ym - 1;
   }
   var _loc3_ = false;
   var _loc1_ = _loc2_ + 1;
   while(_loc1_ <= yx)
   {
      if(updateXY(player,_loc4_,_loc1_))
      {
         _loc3_ = true;
         break;
      }
      _loc1_ += 1;
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ + 1;
      while(_loc1_ <= yx)
      {
         if(updateXY(player,_loc4_ - 2,_loc1_))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ += 1;
      }
   }
   if(!_loc3_)
   {
      _loc1_ = _loc2_ + 1;
      while(_loc1_ <= yx)
      {
         if(updateXY(player,_loc4_ + 2,_loc1_))
         {
            _loc3_ = true;
            break;
         }
         _loc1_ += 1;
      }
   }
}
function onOK(player)
{
   function seltError(str)
   {
      if(!str)
      {
         str = "선택 불가";
      }
      _this["p" + player + "enable"] = true;
      if(player == 1)
      {
         _root.txt = str;
         _root.txtst = 0;
      }
      else
      {
         _root.txt2 = str;
         _root.txtst2 = 0;
      }
   }
   function nextStep()
   {
      if(_root.modo == 1)
      {
         _root["p" + pn + "cpu"] = true;
         _parent.gotoAndPlay("辅助人选");
      }
      else if(_root["p" + pn + "selt"] != "")
      {
         _parent.gotoAndPlay("辅助人选");
      }
   }
   function nextStep2()
   {
      if(_root.modo == 1)
      {
         _root.gostg(_root.stage);
         startgame();
      }
      else if(_root["p" + pn + "sf"] != "")
      {
         _parent.gotoAndPlay("地图");
      }
   }
   function startgame()
   {
      _root.gotoAndStop("游戏场景");
   }
   var pn = player != 1 ? 1 : 2;
   var _loc3_ = _this["p" + pn + "enable"];
   if(isMap)
   {
      if(_root.curStage != "")
      {
         startgame();
      }
   }
   if(isFZ)
   {
      if(_root["p" + player + "selt"] == _root["p" + player + "sf"])
      {
         seltError("중복 선택 불가");
         return undefined;
      }
      if(_root["p" + player + "sf"] != "")
      {
         if(player == 1 && (_root.modo == 2 || _root.modo == 4))
         {
            showP2();
            return undefined;
         }
         if(_this["p" + pn + "enable"] == false)
         {
            nextStep2();
            return undefined;
         }
      }
      else
      {
         seltError("선택 불가");
      }
   }
   else if(_root["p" + player + "selt"] != "")
   {
      if(player == 1 && (_root.modo == 2 || _root.modo == 4))
      {
         showP2();
         return undefined;
      }
      if(_this["p" + pn + "enable"] == false)
      {
         nextStep();
         return undefined;
      }
   }
   else
   {
      seltError("선택 불가");
   }
}
function updateXY(player, x, y)
{
   var _loc5_;
   if(_grid[y][x])
   {
      if(isFZ)
      {
         _loc5_ = _grid[y][x];
         if(_root["p" + player + "selt"] == _loc5_._name)
         {
            return false;
         }
      }
      trace(x + "," + y);
      _this["_p" + player + "selt"] = _grid[y][x];
      _this["curx" + player] = x;
      _this["cury" + player] = y;
      updateSelect(player);
      return true;
   }
   return false;
}
var isFZ;
var isMap;
var isFighter;
var p1enable = true;
var p2enable = false;
var _p1selt;
var _p2selt;
var _this = this;
var _grid = [];
var gs = [];
var curx1 = 0;
var cury1 = 0;
var curx2 = 0;
var cury2 = 0;
var xm = 9999;
var xx = 0;
var ym = 9999;
var yx = 0;
var first;
for(var i in _this)
{
   if(typeof _this[i] == "movieclip")
   {
      var mc = _this[i];
      if(i == "player1" || i == "player2" || i == "_this")
      {
         continue;
      }
      mc.namemc.gotoAndStop(i);
      if(_root.getFighterData(i).isNaruto)
      {
         mc.namemc._xscale *= -1;
         mc.namemc._x = 46;
      }
      var x = int(mc._x / 30);
      var y = int(mc._y / 30);
      if(xm > x)
      {
         xm = x;
      }
      if(xx < x)
      {
         xx = x;
      }
      if(ym > y)
      {
         ym = y;
      }
      if(yx < y)
      {
         yx = y;
      }
      if(!gs[y])
      {
         gs[y] = [];
      }
      gs[y][x] = mc;
      if(!first)
      {
         first = new flash.geom.Point(x,y);
      }
   }
}
_grid = gs;
onEnterFrame = function()
{
   if(p1enable)
   {
      caozuo(1,_root.a,_root.d,_root.w,_root.s,_root.j,_root.k);
   }
   if(p2enable)
   {
      if(_root.modo == 2 or _root.modo == 4)
      {
         caozuo(2,_root.a,_root.d,_root.w,_root.s,_root.j,_root.k);
      }
      else
      {
         caozuo(2,_root.左箭,_root.右箭,_root.上箭,_root.下箭,_root.N1,_root.N2);
      }
   }
};
init(0);
