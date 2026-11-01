function setColor(o)
{
   var _loc1_ = new Color(_this);
   _loc1_.setTransform(o);
}
function resColor()
{
   colors = null;
   _cgap = 1;
   setColor({ra:100,rb:0,ga:100,gb:0,ba:100,bb:0,aa:100,ab:0});
   _this.filters = [];
}
function applyColors()
{
   if(colors && colors.length > 0)
   {
      setColor(colors[_csn]);
      if(++_csn > colors.length - 1)
      {
         _csn = 0;
      }
   }
}
function initWudi()
{
   if(_initwudi)
   {
      return undefined;
   }
   if(!_root.wudi)
   {
      return undefined;
   }
   if(_root.modo == undefined || _parent.useAI == undefined)
   {
      return undefined;
   }
   trace("initwudi" + _root.modo + "," + _parent.useAI);
   _initwudi = true;
   wudi = _root.modo == 1 && _parent.useAI == false;
   if(wudi)
   {
      ql = 300;
   }
}
function followMc(mc, fx, fy, lockx)
{
   trace("followMc , " + fx + "," + fy + "," + lockx);
   if(fx == undefined)
   {
      fx = true;
   }
   if(fy == undefined)
   {
      fy = true;
   }
   if(lockx == undefined)
   {
      lockx = false;
   }
   if(fx == true)
   {
      if(_parent._xscale > 0)
      {
         if(lockx == true)
         {
            if(_parent._x < _root.game["p" + pn]._x)
            {
               mc._x = _root.game["p" + pn]._x - _parent._x;
            }
         }
         else
         {
            mc._x = _root.game["p" + pn]._x - _parent._x;
         }
      }
      else if(lockx == true)
      {
         if(_parent._x > _root.game["p" + pn]._x)
         {
            mc._x = _parent._x - _root.game["p" + pn]._x;
         }
      }
      else
      {
         mc._x = _parent._x - _root.game["p" + pn]._x;
      }
   }
   if(fy == true)
   {
      mc._y = _root.game["p" + pn]._y - _parent._y;
   }
}
function doWanKai()
{
   initCtrl();
   if(_parent.万解)
   {
      hp = _parent.中转.hp;
      ql = _parent.中转.ql;
      if(_parent._name == "p1")
      {
         trace("p1");
         _this.上 = _root.w;
         _this.下 = _root.s;
         _this.左 = _root.a;
         _this.右 = _root.d;
         _this.斩 = _root.j;
         _this.跳 = _root.k;
         _this.冲 = _root.l;
         _this.招 = _root.u;
         _this.必杀 = _root.i;
         _this.换 = _root.o;
      }
      else
      {
         trace("p2");
         _this.上 = _root.上箭;
         _this.下 = _root.下箭;
         _this.左 = _root.左箭;
         _this.右 = _root.右箭;
         _this.斩 = _root.N1;
         _this.跳 = _root.N2;
         _this.冲 = _root.N3;
         _this.招 = _root.N4;
         _this.必杀 = _root.N5;
         _this.换 = _root.N6;
      }
      gotoAndStop("开场");
      play();
   }
}
function loseHp(v)
{
   if(wudi)
   {
      return undefined;
   }
   hp -= v;
}
function onDefence(xgtype)
{
   if(isNaN(xgtype))
   {
      xgtype = 1;
   }
   if(xgtype == 1)
   {
      _root.bdfyxg(_this);
   }
   else
   {
      _root.bdfyxg2(_this);
   }
   updateDirect(true);
   var _loc3_ = _root.game["p" + pn];
   if(_root.to == false)
   {
      loseHp(jhp / 10);
      ql += jhp / 15;
      if(_loc3_.mc.动作 != 3)
      {
         _loc3_.mc.ql += jhp / 10;
      }
   }
   var _loc4_;
   if(_parent.hitWall)
   {
      _loc4_ = Math.abs(_parent._x - _loc3_._x);
      hitNear = _loc4_ < 100;
      if(hitNear)
      {
         hitNear = _parent.scale_X != 1 ? _parent._x > 500 : _parent._x < 500;
      }
   }
   if(_parent.getDepth() > _loc3_.getDepth())
   {
      _parent.swapDepths(_loc3_);
   }
   checkDead(false);
}
function onBeHit()
{
   动作 = -1;
   beida = 1;
   jumped = 0;
   jump = 1;
   hited = 0;
   time = 1;
   play();
}
function onBeHit2(flying)
{
   _root.bdxg(_this);
   if(!flying)
   {
      tdtime += 4;
      if(tdtime < 10)
      {
         tdtime = 10;
      }
   }
   hits++;
   if(hits > 1)
   {
      _root["p" + pn + "hits"].gotoAndPlay("连击");
   }
   hitlosehp();
   updateDirect(true);
   checkDead(flying);
   var _loc3_ = _root.game["p" + pn];
   var _loc4_ = 0.8;
   if(!flying)
   {
      _loc4_ = jhp <= 60 ? 0.1 : 0.5;
   }
   hurtVoice(_loc4_);
   var _loc6_;
   if(_parent.hitWall)
   {
      _loc6_ = Math.abs(_parent._x - _loc3_._x);
      hitNear = _loc6_ < 100;
      if(hitNear)
      {
         hitNear = _parent.scale_X != 1 ? _parent._x > 500 : _parent._x < 500;
      }
   }
   if(_parent.getDepth() > _loc3_.getDepth())
   {
      _parent.swapDepths(_loc3_);
   }
}
function hurtVoice(p)
{
   if(sw)
   {
      if(getTimer() - _dievoicen < 1000)
      {
         return undefined;
      }
      _dievoicen = getTimer();
      dieSnd.start();
      return undefined;
   }
   if(Math.random() > p)
   {
      return undefined;
   }
   if(getTimer() - _lastvoice < 2000)
   {
      return undefined;
   }
   var _loc2_ = _root.getRandInArray(hurtSnds);
   _loc2_.start();
   _lastvoice = getTimer();
}
function hitlosehp()
{
   var _loc2_ = _root.game["p" + pn];
   if(_root.to == false)
   {
      loseHp(jhp);
      ql += jhp / 10;
      if(_loc2_.mc.动作 != 3)
      {
         _loc2_.mc.ql += jhp / 5;
      }
   }
}
function beidax(flying)
{
   applyColors();
   if(_root.zhanting == true)
   {
      return undefined;
   }
   if(hitNear && time <= 6)
   {
      _root.game["p" + pn].moveX((- htx) * 1.2);
   }
   else
   {
      _parent.moveX(- htx);
   }
   _parent.moveY(- yup);
   time++;
   if(time > 13)
   {
      if(yup > 0)
      {
         yup = 0;
      }
      if(!flying)
      {
         htx = 0;
      }
   }
   if(time > 15)
   {
      jump = 0;
   }
   if(flying)
   {
      if(touch == 1)
      {
         if(yup < 0)
         {
            if(hited == 1)
            {
               gotoAndStop("击落地");
               play();
            }
         }
         else if(time > 15)
         {
            gotoAndStop("击落地");
            play();
         }
      }
      return undefined;
   }
   if(time == 0 || tdtime == 0)
   {
      return undefined;
   }
   if(time >= tdtime)
   {
      gotoAndStop("站立");
      play();
   }
}
function beidaStop(flying)
{
   stop();
   hited = 1;
}
function fangyux()
{
   if(_root.zhanting)
   {
      return undefined;
   }
   if(hitNear)
   {
      _root.game["p" + pn].moveX(- htx);
   }
   else
   {
      _parent.moveX(- htx);
   }
}
function onHitDown()
{
   resColor();
   if(sw == true)
   {
      stop();
   }
}
function checkDead(fly)
{
   if(sw)
   {
      return false;
   }
   if(hp <= 0)
   {
      if(_root.modo != 4)
      {
         bdzl = 0;
         sw = true;
         _root.KOplay(pn);
         if(!fly)
         {
            gotoAndStop("击飞");
            play();
         }
         return true;
      }
   }
   return false;
}
function initCtrl()
{
   if(_parent.useAI == undefined)
   {
      return undefined;
   }
   trace("initCtrl: " + _parent.useAI);
   _parent.updateGJL();
   _root.game["p" + pn].updateGJL();
   if(_parent.useAI)
   {
      AImain.gotoAndStop(2);
      _root.airanset = setInterval(randAI,500);
   }
   else
   {
      AImain.gotoAndStop(1);
      AImain.unloadMovie();
   }
}
function on_enterframe()
{
   initWudi();
   if(ql < 0)
   {
      ql = 0;
   }
   if(ql > 300)
   {
      ql = 300;
   }
   if(hp < 0)
   {
      hp = 0;
   }
   if(_root.zhanting)
   {
      return undefined;
   }
   var _loc5_ = _root.game["p" + pn];
   var _loc3_ = (_parent._x - _lastX) * _parent.scale_X;
   if(_loc3_ > 0)
   {
      _loc3_ += _loc5_.vecx / 2;
      _parent.vecx = _loc3_;
   }
   else
   {
      _parent.vecx = 0;
   }
   var _loc7_;
   var _loc4_;
   var _loc10_;
   if(_loc3_ >= 0 && bdmn.hitTest(_root.game["p" + pn].mc.bdmn))
   {
      if(_loc3_ == 0 && _loc5_.vecx == 0)
      {
         _loc3_ = 10;
      }
      _loc7_ = _loc5_.heavy - _parent.heavy;
      if(_loc7_ < 0)
      {
         _loc7_ = 0;
      }
      _loc4_ = _loc3_ / 2 - _loc7_;
      if(_loc4_ < 0)
      {
         _loc4_ = 0;
      }
      _loc10_ = _loc3_ - _loc4_;
      _loc5_._x += _loc4_ * _parent.scale_X;
      _parent.moveX(- _loc10_);
   }
   _lastX = _parent._x;
   var _loc9_ = true;
   var _loc6_ = _parent._y;
   if(_loc6_ == _root.floorY)
   {
      touch = true;
      touchFloor = true;
      return undefined;
   }
   var _loc8_;
   if(_loc6_ < _root.floorY)
   {
      _loc8_ = isHitBan();
      hitBan = _loc8_ != 0;
      if(jump == 1)
      {
         touch = false;
         touchFloor = false;
         return undefined;
      }
      if(hitBan)
      {
         touch = true;
         touchFloor = false;
         _parent._y = _loc8_;
         return undefined;
      }
   }
   if(_loc6_ > _root.floorY - 10)
   {
      _parent._y = _root.floorY;
      touch = true;
      touchFloor = true;
      return undefined;
   }
   if(_loc9_)
   {
      touch = false;
      _parent._y += _root.zhongli;
      if(jumped == 1)
      {
         gotoAndStop("落");
         play();
         jumped = 0;
      }
      if(jumped == 2)
      {
         gotoAndStop("落2");
         play();
         jumped = 0;
      }
   }
}
function isHitBan()
{
   var _loc8_ = _parent._y;
   i = 2;
   var _loc4_;
   var _loc3_;
   var _loc6_;
   var _loc5_;
   var _loc7_;
   while(i <= 30)
   {
      if(_root.game["ban" + i])
      {
         _loc4_ = _root.game["ban" + i];
         _loc3_ = _loc4_._y;
         if(_loc8_ <= _loc3_ && _loc8_ > _loc3_ - 10)
         {
            _loc6_ = _parent._x;
            _loc5_ = _loc4_._x;
            _loc7_ = _loc4_._width;
            if(_loc6_ >= _loc5_ && _loc6_ <= _loc5_ + _loc7_)
            {
               return _loc3_;
            }
         }
      }
      i++;
   }
   return 0;
}
function randAI()
{
   var _loc2_ = 100 * _root.AI;
   attran = Math.random() * _loc2_;
   defran = Math.random() * _loc2_;
   goran = Math.random() * _loc2_;
   jumpran = Math.random() * _loc2_;
   bisharan = Math.random() * _loc2_;
}
function wankai()
{
   _parent.万解 = true;
   _parent.中转.ql = ql;
   _parent.中转.hp = hp;
   if(!wudi)
   {
      clearInterval(_root.feiint);
      _root.feiint = setInterval(feixue,1000);
   }
   _parent.nextFrame();
   _root._y = 0;
}
function wankai_start()
{
   动作 = 3;
   bs = 1;
   ql -= 300;
   jump = 1;
   _root.cbsd(pn);
}
function wankai_end()
{
   if(_parent.万解)
   {
      _root.cbsw(pn);
      bs = 0;
      _parent.万解 = false;
   }
}
function updateDirect(bhit)
{
   if(bhit)
   {
      _parent.scale_X = _root.game["p" + pn]._xscale >= 0 ? -1 : 1;
   }
   else
   {
      _parent.scale_X = _parent._x <= _root.game["p" + pn]._x ? 1 : -1;
   }
   _parent._xscale = _parent.scale_X * 100;
}
var khit = 0;
var jump = 0;
var movspeed = 0;
var jumped = 1;
var yup = 0;
var htx = 0;
var tdtime = 0;
var bdzl = 0;
var hited = 0;
var 动作 = 0;
var beida = 0;
var bs = 0;
var sw;
var time = 0;
var touch = true;
var touchFloor = true;
var wudi;
var canHide = true;
var speed = spd;
var _this = this;
var 动作 = 0;
var hurtSnds = [];
var hurtSndAttach = ["voice_hurt1","voice_hurt2"];
var dieSnd = new Sound(_this);
dieSnd.attachSound("voice_die");
var i = 0;
while(i < hurtSndAttach.length)
{
   var hv = hurtSndAttach[i];
   var snd = new Sound(_this);
   snd.attachSound(hv);
   hurtSnds.push(snd);
   i++;
}
resColor();
_parent.scale_X = _parent._xscale <= 0 ? -1 : 1;
var inited;
if(!inited)
{
   trace("inited");
   inited = true;
   _lastX = 0;
   pn = _parent._name != "p1" ? 1 : 2;
   doWanKai();
   if(!_parent.万解)
   {
      updateDirect();
   }
}
var colors;
var _cgap = 0;
var _csn = 0;
var _initwudi;
var hitNear = false;
var _lastvoice = 0;
var _dievoicen = 0;
var _lastX;
var hitBan;
feixue = function()
{
   if(_root.zhanting == false)
   {
      if(_this.hp > _root.maxhp / 5)
      {
         loseHp(10);
      }
   }
};
