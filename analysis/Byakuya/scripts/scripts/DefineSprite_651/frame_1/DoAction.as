function gameRunning()
{
   return _root.zhanting == false && _root.game["p" + _parent.pn].mc.sw == false;
}
function wankai()
{
   if(!_parent._parent.useAI)
   {
      return _parent.ql >= 300 && _parent.kis(_parent.斩) && _parent.kis(_parent.跳);
   }
   return false;
}
function moveLeft()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.左);
   }
   if(_parent._parent._x > _root.game["p" + _parent.pn]._x + 20)
   {
      return _parent.goran < 120;
   }
   return false;
}
function moveRight()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.右);
   }
   if(_parent._parent._x < _root.game["p" + _parent.pn]._x - 20)
   {
      return _parent.goran < 120;
   }
   return false;
}
function airhit(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.斩);
   }
   if(combo === true)
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 120;
      }
      return false;
   }
   if(_parent.AImain.tkanmian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 120;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 100;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function airMagichit(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.招);
   }
   if(combo === true)
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 120;
      }
      return false;
   }
   if(_parent.AImain.tkanmian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("tz") > 10)
      {
         return _parent.attran < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function holdJ()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.斩);
   }
   if(_root.game["p" + _parent.pn].mc.动作 == -1)
   {
      return _parent.attran < 120 == false;
   }
   if(_root.game["p" + _parent.pn].mc.动作 == 2)
   {
      return _parent.attran < 100;
   }
   return _parent.attran > 100 && _parent.attran < 300;
}
function holdU()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.招);
   }
   if(_root.game["p" + _parent.pn].mc.动作 == -1)
   {
      return _parent.attran < 120 == false;
   }
   if(_root.game["p" + _parent.pn].mc.动作 == 2)
   {
      return _parent.attran < 100;
   }
   return _parent.attran > 100 && _parent.attran < 300;
}
function nornalhit(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.斩) && !_parent.kis(_parent.跳) && !_parent.kis(_parent.上) && !_parent.kis(_parent.下);
   }
   if(combo === true)
   {
      return combohitAI();
   }
   if(_parent.AImain.kanmian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 120;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 100;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function combohitAI(act)
{
   if(_root.game["p" + _parent.pn].mc.动作 == -1)
   {
      return _parent.attran < 120;
   }
   if(_root.game["p" + _parent.pn].mc.动作 < 2)
   {
      return _parent.attran > 50 && _parent.attran < 100;
   }
   if(act != undefined && isPoFangAct(act))
   {
      return _parent.attran < 90;
   }
   if(_root.game["p" + _parent.pn].mc.动作 == 2)
   {
      return _parent.attran > 80 && _parent.attran < 150;
   }
   return false;
}
function magichit1(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.招);
   }
   if(combo === true)
   {
      return combohitAI("zh1");
   }
   if(_parent.AImain.zh1mian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("zh1"))
      {
         return _parent.attran < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 70;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 50;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function magichit2(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.下) && _parent.kis(_parent.招);
   }
   if(combo === true)
   {
      return combohitAI("zh2");
   }
   if(_parent.AImain.zh2mian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("zh2"))
      {
         return _parent.attran < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 80;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 55;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function magichit3(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.上) && _parent.kis(_parent.招);
   }
   if(combo === true)
   {
      return combohitAI("zh3");
   }
   if(_parent.AImain.zh3mian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("zh3"))
      {
         return _parent.attran < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 80;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 50;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function skill1(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.下) && _parent.kis(_parent.斩);
   }
   if(combo === true)
   {
      return combohitAI("kj1");
   }
   if(_parent.AImain.kj1mian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("kj1"))
      {
         return _parent.attran < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 80;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 50;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function skill2(combo)
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.上) && _parent.kis(_parent.斩);
   }
   if(combo === true)
   {
      return combohitAI("kj2");
   }
   if(_parent.AImain.kj2mian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("kj2"))
      {
         return _parent.attran < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.attran < 80;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.attran < 50;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.attran > 200 && _parent.attran < 300;
      }
   }
   return false;
}
function jump()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.跳) && !_parent.kis(_parent.斩);
   }
   if(_root.game["p" + _parent.pn].mc.动作 < 3)
   {
      if(_root.game["p" + _parent.pn]._y < _parent._parent._y - 20)
      {
         return _parent.jumpran < 100;
      }
      return _parent.jumpran > 100 && _parent.jumpran < 130;
   }
   return false;
}
function jumpDown()
{
   if(_parent.touchFloor)
   {
      return false;
   }
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.下) && _parent.kis(_parent.跳);
   }
   if(_root.game["p" + _parent.pn].mc.动作 < 3)
   {
      if(_root.game["p" + _parent.pn]._y > _parent._parent._y + 50)
      {
         return _parent.jumpran < 100;
      }
      return _parent.jumpran > 100 && _parent.jumpran < 130;
   }
   return false;
}
function rush()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.冲) && !_parent.kis(_parent.上) && !_parent.kis(_parent.下);
   }
   var _loc3_;
   if(_root.game["p" + _parent.pn].mc.动作 == 1)
   {
      return _parent.goran < 40;
   }
   if(Math.abs(_root.game["p" + _parent.pn]._x - _parent._parent._x) > 80)
   {
      _loc3_ = _parent.goran < 80;
      if(_loc3_)
      {
         _parent._parent.scale_X = _parent._parent._x <= _root.game["p" + _parent.pn]._x ? 1 : -1;
         _parent._parent._xscale = _parent._parent.scale_X * 100;
         return true;
      }
   }
   return _parent.goran > 120 && _parent.goran < 200;
}
function hide()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.下) && _parent.kis(_parent.冲);
   }
   var _loc3_;
   if(_root.game["p" + _parent.pn].mc.动作 == 1)
   {
      return _parent.goran < 50;
   }
   return _parent.goran > 100 && _parent.goran < 200;
}
function defence()
{
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.下);
   }
   if(!_parent.canhit)
   {
      return false;
   }
   if(_root.game["p" + _parent.pn].mc.动作 == 3 || _root.game["p" + _parent.pn + "fz"].动作 == 1)
   {
      return _parent.defran < 130;
   }
   if(_root.game["p" + _parent.pn].mc.动作 == 1)
   {
      return _parent.defran < 100;
   }
   return false;
}
function standup()
{
   if(_parent.sw == false)
   {
      if(!_parent._parent.useAI)
      {
         return _parent.kis(_parent.冲);
      }
      return _parent.goran < 40;
   }
   return false;
}
function zhaoHuan()
{
   if(_parent.ql < 100)
   {
      return false;
   }
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.换);
   }
   if(_root.game["p" + _parent.pn].mc.动作 < 2)
   {
      return _parent.attran > 90 && _parent.bisharan < 100;
   }
   if(_root.game["p" + _parent.pn].mc.动作 == 2)
   {
      return _parent.attran > 200 && _parent.attran < 220;
   }
   return false;
}
function bisha(combo, qi)
{
   if(isNaN(qi))
   {
      qi = 100;
   }
   if(_parent.ql < qi)
   {
      return false;
   }
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.必杀);
   }
   if(combo === true)
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 90;
      }
      return false;
   }
   if(_parent.AImain.bsmian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("bs"))
      {
         return _parent.bisharan < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 80;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.bisharan > 95;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.bisharan > 200 && _parent.bisharan < 250;
      }
   }
   return false;
}
function bishaUP(combo, qi)
{
   if(isNaN(qi))
   {
      qi = 100;
   }
   if(_parent.ql < qi)
   {
      return false;
   }
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.上) && _parent.kis(_parent.必杀);
   }
   if(combo === true)
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 90;
      }
      return false;
   }
   if(_parent.AImain.sbsmian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("sbs"))
      {
         return _parent.bisharan < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 100;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.bisharan > 95;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.bisharan > 200 && _parent.bisharan < 250;
      }
   }
   return false;
}
function bishaAir(combo, qi)
{
   if(isNaN(qi))
   {
      qi = 100;
   }
   if(_parent.ql < qi)
   {
      return false;
   }
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.必杀);
   }
   if(combo === true)
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 90;
      }
      return false;
   }
   if(_parent.AImain.absmian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("kbs"))
      {
         return _parent.bisharan < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 80;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.bisharan > 95;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.bisharan > 200 && _parent.bisharan < 250;
      }
   }
   return false;
}
function bishaSuper(combo, qi)
{
   if(isNaN(qi))
   {
      qi = 300;
   }
   if(_parent.ql < qi)
   {
      return false;
   }
   if(!_parent._parent.useAI)
   {
      return _parent.kis(_parent.下) && _parent.kis(_parent.必杀);
   }
   if(combo === true)
   {
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 80;
      }
      return false;
   }
   if(_parent.AImain.cbsmian.hitTest(_root.game["p" + _parent.pn].mc.bdmn))
   {
      if(isPoFangAct("cbs"))
      {
         return _parent.bisharan < 60;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == -1)
      {
         return _parent.bisharan < 90;
      }
      if(_root.game["p" + _parent.pn].mc.动作 < 2)
      {
         return _parent.bisharan > 95;
      }
      if(_root.game["p" + _parent.pn].mc.动作 == 2)
      {
         return _parent.bisharan > 200 && _parent.bisharan < 250;
      }
   }
   return false;
}
function onJumping(step)
{
   if(isNaN(step))
   {
      step = 1;
   }
   if(step == 1 || step == 4)
   {
      if(!jumpinggg)
      {
         jumpinggg = true;
         js = _parent.jumpPower;
         _root.jumpxg(_parent._parent);
      }
   }
   else
   {
      jumpinggg = false;
   }
   if(gameRunning())
   {
      if(moveLeft())
      {
         _parent._parent._x -= _parent.speed;
      }
      if(moveRight())
      {
         _parent._parent._x += _parent.speed;
      }
      if(step == 1 || step == 2)
      {
         if(rush())
         {
            _parent.gotoAndPlay("瞬步");
         }
      }
      if(step == 2 || step == 3)
      {
         if(jump())
         {
            _parent.gotoAndPlay("跳2");
         }
      }
      if(_parent.khit == 0)
      {
         if(airhit())
         {
            _parent.gotoAndPlay("跳砍");
         }
         if(airMagichit())
         {
            _parent.gotoAndPlay("跳招");
         }
         if(bishaAir())
         {
            _parent.gotoAndPlay("空中必杀");
         }
      }
      if(step == 1 || step == 4)
      {
         js -= 1;
      }
      if(step == 1 || step == 2 || step == 4 || step == 5)
      {
         _parent._parent._y -= js;
      }
   }
   if(_root.zhanting == false)
   {
      if(step == 3 || step == 6)
      {
         if(_parent.touch == true)
         {
            _root.luodixg(_parent._parent);
            _parent.gotoAndPlay("落地");
         }
      }
   }
}
function doDropDown()
{
   if(jumpDown())
   {
      _parent._parent._y += _root.zhongli;
      _parent.jumped = 0;
      _parent.fall = true;
      _parent.gotoAndPlay("落2");
   }
}
function onDashing(spdPlus)
{
   if(isNaN(spdPlus))
   {
      spdPlus = 2;
   }
   moveX(_parent.speed * spdPlus);
   if(!touchFloor)
   {
      if(bishaAir())
      {
         _parent.gotoAndPlay("空中必杀");
      }
   }
   else
   {
      if(bishaUP())
      {
         _parent.gotoAndPlay("上必杀");
      }
      if(bishaSuper())
      {
         _parent.gotoAndPlay("超必杀");
      }
      if(bisha())
      {
         _parent.gotoAndPlay("必杀");
      }
   }
}
function onDefence()
{
   if(defence())
   {
      _parent.gotoAndPlay("防御2");
   }
   if(skill1())
   {
      _parent.gotoAndPlay("砍技1");
   }
   if(magichit2())
   {
      _parent.gotoAndPlay("招2");
   }
   if(bishaSuper())
   {
      _parent.gotoAndPlay("超必杀");
   }
   doDropDown();
}
function doStand()
{
   if(!standed)
   {
      _parent.resColor();
      standed = true;
   }
   if(defence())
   {
      _parent.gotoAndPlay("防御");
      return undefined;
   }
   if(nornalhit())
   {
      _parent.gotoAndPlay("砍1");
   }
   if(skill2())
   {
      _parent.gotoAndPlay("砍技2");
   }
   if(skill1())
   {
      _parent.gotoAndPlay("砍技1");
   }
   if(magichit3())
   {
      _parent.gotoAndPlay("招3");
   }
   if(magichit2())
   {
      _parent.gotoAndPlay("招2");
   }
   if(magichit1())
   {
      _parent.gotoAndPlay("招1");
   }
}
function doAllAction(special)
{
   if(special == undefined)
   {
      special = "";
   }
   if(defence())
   {
      _parent.gotoAndPlay("防御");
   }
   if(nornalhit())
   {
      _parent.gotoAndPlay("砍1");
   }
   if(wankai())
   {
      _parent.gotoAndPlay("万解");
   }
   if(skill2())
   {
      _parent.gotoAndPlay("砍技2");
   }
   if(skill1())
   {
      _parent.gotoAndPlay("砍技1");
   }
   if(magichit3())
   {
      _parent.gotoAndPlay("招3");
   }
   if(magichit2())
   {
      _parent.gotoAndPlay("招2");
   }
   if(magichit1())
   {
      _parent.gotoAndPlay("招1");
   }
   if(bishaSuper())
   {
      _parent.gotoAndPlay("超必杀");
   }
   if(bishaUP())
   {
      _parent.gotoAndPlay("上必杀");
   }
   if(bisha())
   {
      _parent.gotoAndPlay("必杀");
   }
   if(zhaoHuan())
   {
      _parent.gotoAndPlay("招换");
   }
   var _loc2_ = moveLeft();
   var _loc3_ = moveRight();
   if(_loc2_)
   {
      _parent._parent._xscale = -100;
      _parent._parent.scale_X = -1;
   }
   if(_loc3_)
   {
      _parent._parent._xscale = 100;
      _parent._parent.scale_X = 1;
   }
   if(rush())
   {
      _parent.gotoAndPlay("瞬步");
   }
   if(jump())
   {
      _parent.gotoAndPlay("跳");
   }
   if(_loc2_)
   {
      _parent._parent._x -= _parent.speed;
      _parent.gotoAndPlay("走");
   }
   if(_loc3_)
   {
      _parent._parent._x += _parent.speed;
      _parent.gotoAndPlay("走");
   }
   if(!_loc2_ && !_loc3_)
   {
      _parent.updateDirect();
   }
   doDropDown();
}
function isPoFangAct(name)
{
   return _parent._parent._curGJL[name + "zl"] > 10;
}
function moveX(spd)
{
   _parent._parent.moveX(spd);
}
function moveY(spd)
{
   _parent._parent.moveY(- spd);
}
var js = 0;
var jumpinggg;
var standed = false;
var allF = 0;
var walkF = 0;
