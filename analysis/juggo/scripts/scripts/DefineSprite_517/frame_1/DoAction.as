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
   if(_parent.getDepth() > _loc3_.getDepth())
   {
      _parent.swapDepths(_loc3_);
   }
   checkDead(false);
}
function onBeHit0()
{
   动作 = -1;
   beida = 1;
   jumped = 0;
   jump = 1;
   hited = 1;
   time = 0;
   play();
}
function onBeHit(flying)
{
   onBeHit0();
   _root.bdxg(_this);
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
   var _loc5_;
   if(_parent.hitWall)
   {
      _loc5_ = Math.abs(_parent._x - _loc3_._x);
      hitNear = _loc5_ < 100;
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
   if(hitNear && time <= 5 && htx > 0)
   {
      _root.game["p" + pn].moveX((- htx) * 1.5);
   }
   else
   {
      _parent.moveX(- htx);
   }
   _parent.moveY(- yup);
   hstm++;
   if(!flying && hstm < 20)
   {
      doHurtSkill();
   }
   time++;
   if(time > 13)
   {
      yup = 0;
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
   if(time == 0 || tdtime == 0 || isNaN(tdtime))
   {
      play();
      return undefined;
   }
   if(time >= tdtime)
   {
      play();
   }
}
function hurtSkill()
{
   if(hp <= 0)
   {
      return false;
   }
   if(sw)
   {
      return false;
   }
   if(ql < 100)
   {
      return false;
   }
   if(_root.game["p" + pn].mc.动作 == 3)
   {
      return false;
   }
   if(!_parent.useAI)
   {
      return kis(换);
   }
   return goran < 30;
}
function doHurtSkill()
{
   if(hurtSkling)
   {
      return undefined;
   }
   if(!hurtSkill())
   {
      return undefined;
   }
   ql -= 100;
   hurtSkling = true;
   wdFrame = 0;
   wdFrameX = 10;
   var _loc3_ = _root.game["p" + pn];
   if(_parent.getDepth() < _loc3_.getDepth())
   {
      _parent.swapDepths(_loc3_);
   }
   if(_parent.isNaruto)
   {
      _root.bsd(pn,"XG_tishen",false);
      _parent.moveX(150);
      updateDirect();
      _root.addChildXG(_parent,"XG_tishen2",0,0);
      gotoAndStop("站立");
      play();
      setTimeout(function()
      {
         _root.bsw(pn,false);
      }
      ,800);
   }
   else
   {
      _root.bsd(pn,"XG_bsq",false);
      setTimeout(function()
      {
         hurtSkling = true;
         _root.bsw(pn,false);
         gotoAndStop("招换");
         play();
         _root.addStgHit(pn,"XG_baoqi",{pw:80,zl:5,yup:0,hitx:15,hdtime:0,htype:"击飞"});
      }
      ,600);
   }
}
function doZhaoHuan()
{
   if(hurtSkling)
   {
      return undefined;
   }
   _root.yfgj(_parent._name);
   bs = 1;
   ql -= 100;
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
   _parent.moveX(- htx);
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
   if(_parent._x < 20)
   {
      _parent._x = 20;
   }
   if(_parent._x > _root.mapSizeX - 30)
   {
      _parent._x = _root.mapSizeX - 30;
   }
   if(dashing)
   {
      onDashing();
      if(_parent._y > _root.floorY)
      {
         _parent._y = _root.floorY;
      }
      _lastX = _parent._x;
      return undefined;
   }
   if(_root.zhanting)
   {
      return undefined;
   }
   if(wdFrameX > 0 && !isNaN(wdFrameX) && !isNaN(wdFrame))
   {
      canhit = false;
      if(++wdFrame >= wdFrameX)
      {
         canhit = true;
         wdFrame = wdFrameX = 0;
      }
   }
   if(!dashing)
   {
      doDashX();
   }
   var _loc6_ = _root.game["p" + pn];
   var _loc4_ = _parent._x - _lastX;
   if(_loc4_ > 30)
   {
      _loc4_ = 30;
   }
   if(_loc4_ < -30)
   {
      _loc4_ = -30;
   }
   var _loc3_ = _loc4_ * _parent.scale_X;
   if(_loc3_ > 0)
   {
      _loc3_ += _loc6_.vecx / 2;
      _parent.vecx = _loc3_;
   }
   else
   {
      _parent.vecx = 0;
   }
   var _loc8_;
   var _loc5_;
   var _loc11_;
   if(airBody == false && _root.game["p" + pn].mc.airBody == false)
   {
      if(_loc3_ >= 0 && bdmn.hitTest(_root.game["p" + pn].mc.bdmn))
      {
         if(_loc3_ == 0 && _loc6_.vecx == 0)
         {
            _loc3_ = 10;
         }
         _loc8_ = _loc6_.heavy - _parent.heavy;
         if(_loc8_ < 0)
         {
            _loc8_ = 0;
         }
         _loc5_ = _loc3_ / 2 - _loc8_;
         if(_loc5_ < 0)
         {
            _loc5_ = 0;
         }
         _loc11_ = _loc3_ - _loc5_;
         _loc6_._x += _loc5_ * _parent.scale_X;
         _parent.moveX(- _loc11_);
      }
   }
   _lastX = _parent._x;
   var _loc10_ = true;
   var _loc7_ = _parent._y;
   if(_loc7_ == _root.floorY)
   {
      touch = true;
      touchFloor = true;
      return undefined;
   }
   var _loc9_;
   if(_loc7_ < _root.floorY)
   {
      _loc9_ = isHitBan();
      hitBan = _loc9_ != 0;
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
         _parent._y = _loc9_;
         return undefined;
      }
   }
   if(_loc7_ > _root.floorY - 10)
   {
      _parent._y = _root.floorY;
      touch = true;
      touchFloor = true;
      return undefined;
   }
   if(_loc10_)
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
function zhaoHuan()
{
   if(hp <= 0)
   {
      return false;
   }
   if(ql < 100)
   {
      return false;
   }
   if(!touchFloor && !hitBan)
   {
      return false;
   }
   if(jump == 1)
   {
      return false;
   }
   if(动作 != 0 && 动作 != 2)
   {
      return false;
   }
   if(_root.game["p" + pn].mc.sw == true)
   {
      return false;
   }
   if(_root.game[_parent._name + "fz"].attacking === true)
   {
      return false;
   }
   if(!_parent.useAI)
   {
      return kis(换);
   }
   if(_root.game["p" + pn].mc.动作 < 2)
   {
      return attran > 90 && bisharan < 100;
   }
   if(_root.game["p" + pn].mc.动作 == 2)
   {
      return attran > 200 && attran < 220;
   }
   return false;
}
function dash()
{
   if(hp <= 0)
   {
      return false;
   }
   if(sw)
   {
      return false;
   }
   if(ql < dashQL)
   {
      return false;
   }
   if(动作 != 0 && 动作 != 1 && 动作 != 2)
   {
      return false;
   }
   if(_root.game["p" + pn].mc.sw == true)
   {
      return false;
   }
   var _loc4_ = _root.game["p" + pn];
   if(!_parent.useAI)
   {
      if(kis(冲))
      {
         if(kis(上))
         {
            dashX = 0;
            dashY = -14;
            return true;
         }
         if(kis(下))
         {
            if(hitBan || touch)
            {
               dashX = 10;
               dashY = 0;
               updateDirect();
            }
            else
            {
               dashX = 0;
               dashY = 12;
            }
            return true;
         }
         return false;
      }
   }
   if(!hitBan && !touch)
   {
      return false;
   }
   var _loc3_;
   var _loc5_ = Math.abs(_loc4_._x - _parent._x);
   if(动作 == 1 && _loc4_.mc.动作 == -1)
   {
      _loc3_ = goran < 40;
   }
   if(动作 == 2 && _loc4_.mc.动作 == 1)
   {
      _loc3_ = goran < 30;
   }
   if(动作 == 1)
   {
      _loc3_ = goran > 120 && goran < 140;
   }
   if(_loc3_)
   {
      dashX = 10;
      dashY = 0;
      updateDirect();
      return true;
   }
   return false;
}
function doDashX()
{
   if(dash())
   {
      dashing = true;
      ql -= dashQL;
      dashF = 0;
      _root.bsd(pn,"XG_xdash",false);
   }
}
function onDashing()
{
   if(++dashF < 10)
   {
      if(dashY != 0)
      {
         _parent.moveY(dashY);
         hitBan = false;
         touch = false;
         gotoAndStop("落");
      }
      else
      {
         _parent.moveX(dashX);
         gotoAndStop("走");
      }
      _parent.showdow({R:20,G:-100,B:255});
   }
   else
   {
      _root.bsw(pn,false);
      dashing = false;
      updateDirect();
      if(dashY != 0)
      {
         gotoAndStop("落2");
         play();
      }
      else
      {
         updateDirect();
         gotoAndStop("站立");
         play();
      }
   }
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
var touch;
var touchFloor;
var wudi;
var canHide = true;
var speed = spd;
var canhit = true;
var wdFrame;
var wdFrameX;
var hits = 0;
var airBody = false;
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
_parent._visible = true;
_visible = true;
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
var hstm = 0;
var hurtSkling = false;
var _lastX;
var hitBan;
var dashQL = 100;
var dashing;
var dashX;
var dashY;
var dashF = 0;
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
