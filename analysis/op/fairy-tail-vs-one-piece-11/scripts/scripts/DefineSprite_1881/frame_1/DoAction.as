function kaichang()
{
   if(_root.p2loaded == false)
   {
      return undefined;
   }
   var _loc2_ = _root.game.p1.mc.kcplayed;
   var _loc3_ = _root.game.p2.mc.kcplayed;
   switch(curStep)
   {
      case 0:
         if(_loc2_ == 0 && _loc3_ == 0)
         {
            goStep(1);
         }
         break;
      case 1:
         if(_loc2_ == 0)
         {
            goStep(2);
         }
         break;
      case 2:
         if(_loc2_ == 2)
         {
            if(_loc3_ == 0)
            {
               goStep(3);
            }
         }
         else if(_root.game.p1.mc._currentframe < 10)
         {
            goStep(2);
         }
         break;
      case 3:
         if(_loc3_ == 2)
         {
            goStep(4);
         }
         else if(_root.game.p2.mc._currentframe < 10)
         {
            goStep(3);
         }
      default:
         return;
   }
}
function goStep(step)
{
   curStep = step;
   switch(step)
   {
      case 1:
         _root.game.p1.mc.gotoAndStop("开场");
         _root.game.p2.mc.gotoAndStop("开场");
         _root.qjxg.gotoAndPlay("开");
         _root.weathermc.gotoAndStop(_root.weather);
         break;
      case 2:
         _root.焦点 = "p1";
         _root.game.p1.mc.gotoAndPlay("开场");
         break;
      case 3:
         _root.焦点 = "p2";
         _root.game.p2.mc.gotoAndPlay("开场");
         break;
      case 4:
         _root.焦点 = "all";
         _root.ready.play();
         clearInterval(_root.kcint);
      default:
         return;
   }
}
function renderSkip()
{
   if(curStep > 1 && curStep < 4)
   {
      if(Key.isDown(_root.j) || Key.isDown(_root.N1))
      {
         curStep = 4;
         _root.ready.gotoAndStop(1);
         _root.qjxg.gotoAndPlay("skipintro");
      }
   }
}
function zdbx()
{
   if(_root.p2loaded == true)
   {
      if(_root.game.p1.mc.beida == 0)
      {
         _root.game.p1.mc.hp = _root.maxhp;
         _root.game.p1.mc.ql = 300;
      }
      if(_root.game.p2.mc.beida == 0)
      {
         _root.game.p2.mc.hp = _root.maxhp;
         _root.game.p2.mc.ql = 300;
      }
   }
}
function getCenter(n1, n2)
{
   var _loc1_;
   var _loc2_;
   if(n1 > n2)
   {
      _loc1_ = n2;
      _loc2_ = n1;
   }
   else
   {
      _loc1_ = n1;
      _loc2_ = n2;
   }
   return _loc1_ + (_loc2_ - _loc1_) / 2;
}
_root.rounds = 1;
_root.zhanting = true;
_root.game.gotoAndStop(_root.curStage);
_root.bg.gotoAndStop(_root.curStage);
_root.qjxg.gotoAndStop("关闭");
_root.焦点 = "p1";
_root.p1ws = _root.p2ws = 1;
_root.kcint = setInterval(kaichang,500);
if(_root.modo == 4)
{
   _root.zdbxint = setInterval(zdbx,1000);
}
var curStep = 0;
_root.gamePlayers = [];
_root.gamePlayers.push(_root.game.p1);
_root.gamePlayers.push(_root.game.p2);
_root.gamePlayers.push(_root.game.p1fz);
_root.gamePlayers.push(_root.game.p2fz);
var _tweenX = 0.5;
var _scaleMin = 1;
var _jlMax = 500;
var _lockMin = 0;
var _lockMax = 0;
onEnterFrame = function()
{
   renderSkip();
   _root.renderIng();
   if(_root.loop > 100)
   {
      _root.loop = 10;
   }
   var _loc4_ = 20;
   var _loc5_ = _root.mapSizeX - 30;
   var _loc3_ = 0;
   var _loc2_;
   while(_loc3_ < _root.gamePlayers.length)
   {
      _loc2_ = _root.gamePlayers[_loc3_];
      if(_loc2_._x < _loc4_)
      {
         _loc2_._x = _loc4_;
      }
      if(_loc2_._x > _loc5_)
      {
         _loc2_._x = _loc5_;
      }
      _loc2_.hitWall = !(_loc2_._x > _loc4_ && _loc2_._x < _loc5_);
      _loc3_ = _loc3_ + 1;
   }
   var _loc17_ = Math.abs(_root.game.p1._x - _root.game.p2._x);
   if(_lockMin > 0 && _lockMax > 0)
   {
      if(_loc17_ < _jlMax)
      {
         _lockMin = _lockMax = 0;
      }
      else
      {
         if(_root.game.p1._x < _lockMin)
         {
            _root.game.p1._x = _lockMin;
         }
         if(_root.game.p2._x < _lockMin)
         {
            _root.game.p2._x = _lockMin;
         }
         if(_root.game.p1._x > _lockMax)
         {
            _root.game.p1._x = _lockMax;
         }
         if(_root.game.p2._x > _lockMax)
         {
            _root.game.p2._x = _lockMax;
         }
      }
   }
   else if(_loc17_ >= _jlMax)
   {
      _lockMin = Math.min(_root.game.p1._x,_root.game.p2._x);
      _lockMax = Math.max(_root.game.p1._x,_root.game.p2._x);
   }
   var _loc28_ = (- _root.mapSizeX) / 2;
   var _loc24_ = _root.mapSizeX;
   var _loc13_ = _root.game.p1._x;
   var _loc11_ = _root.game.p1._y;
   var _loc12_ = _root.game.p2._x;
   var _loc16_ = _root.game.p2._y;
   var _loc15_ = 0;
   var _loc14_ = 0;
   var _loc6_ = 0;
   var _loc26_;
   var _loc25_;
   var _loc27_;
   var _loc19_;
   var _loc18_;
   switch(_root.焦点)
   {
      case "all":
         _loc15_ = getCenter(_loc13_,_loc12_);
         _loc14_ = getCenter(_loc11_,_loc16_);
         _loc26_ = Math.abs(_loc13_ - _loc12_);
         _loc25_ = Math.abs(_loc11_ - _loc16_);
         _loc27_ = Math.max(_loc26_,_loc25_);
         _loc19_ = 1000;
         _loc18_ = _loc19_ - _loc27_;
         if(_loc18_ <= 0)
         {
            _loc6_ = 0.5;
         }
         else
         {
            _loc6_ = 2 * (_loc18_ / _loc19_);
         }
         break;
      case "p1":
         _loc15_ = _loc13_;
         _loc14_ = _loc11_;
         _loc6_ = 2;
         break;
      case "p2":
         _loc15_ = _loc12_;
         _loc14_ = _loc16_;
         _loc6_ = 2;
   }
   if(_loc6_ < _scaleMin)
   {
      _loc6_ = _scaleMin;
   }
   var _loc7_ = 300 - _loc15_ * _loc6_;
   var _loc10_ = 300 - _loc14_ * _loc6_;
   var _loc21_ = 620 - _loc24_ * _loc6_;
   if(_loc7_ > 0)
   {
      _loc7_ = 0;
   }
   if(_loc7_ < _loc21_)
   {
      _loc7_ = _loc21_;
   }
   var _loc20_ = 400;
   if(_loc10_ < _loc20_)
   {
      _loc10_ = _loc20_;
   }
   var _loc0_;
   var _loc22_;
   var _loc8_;
   var _loc23_;
   var _loc9_;
   if(_loc6_ < 1.5)
   {
      var _temp_2 = _root.Arw_1P;
      var _temp_1 = "_visible";
      _root.Arw_2P._visible = _loc0_ = true;
      _temp_2[_temp_1] = _loc0_;
      _loc22_ = _loc7_ + _loc13_ * _loc6_;
      _loc8_ = _loc10_ + (_loc11_ - 80) * _loc6_;
      _loc23_ = _loc7_ + _loc12_ * _loc6_;
      _loc9_ = _loc10_ + (_loc16_ - 80) * _loc6_;
      if(_loc8_ < 60)
      {
         _loc8_ = 60;
      }
      if(_loc8_ > 390)
      {
         _loc8_ = 390;
      }
      if(_loc9_ < 60)
      {
         _loc9_ = 60;
      }
      if(_loc9_ > 390)
      {
         _loc9_ = 390;
      }
      _root.Arw_1P._x = _loc22_;
      _root.Arw_1P._y = _loc8_;
      _root.Arw_2P._x = _loc23_;
      _root.Arw_2P._y = _loc9_;
   }
   else
   {
      var _temp_4 = _root.Arw_1P;
      var _temp_3 = "_visible";
      _root.Arw_2P._visible = _loc0_ = false;
      _temp_4[_temp_3] = _loc0_;
   }
   _root.game._x += (_loc7_ - _root.game._x) * _tweenX;
   _root.game._y += (_loc10_ - _root.game._y) * _tweenX;
   _root.game._xscale += (_loc6_ * 100 - _root.game._xscale) * _tweenX;
   _root.game._yscale += (_loc6_ * 100 - _root.game._yscale) * _tweenX;
};
