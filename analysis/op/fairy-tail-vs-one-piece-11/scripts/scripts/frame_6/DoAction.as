function yfgj(nam)
{
   var _loc3_ = _root.game[nam + "fz"];
   var _loc2_ = _root.game[nam];
   var _loc6_ = nam != "p1" ? _root.game.p1 : _root.game.p2;
   _loc3_.attacking = true;
   var _loc5_ = _loc2_._x >= _loc6_._x ? -1 : 1;
   _loc3_._x = _loc2_._x - 20 * (_loc2_._xscale <= 0 ? -1 : 1);
   _loc3_._y = _loc2_._y;
   _loc3_._xscale = _loc5_ * 100;
   _root.game[nam + "fz"].gotoAndPlay(2);
}
function removeFZ(mc)
{
   mc.attacking = false;
   mc.动作 = 0;
   fzccXg(mc);
   mc.stop();
}
function gostg(stg)
{
   if(stgObj && stgObj.stg == stg)
   {
      _root.p2selt = stgObj.p2selt;
      _root.curStage = stgObj.curStage;
      return undefined;
   }
   var _loc4_ = _root.getFighterData(_root.p1selt);
   var _loc2_ = _loc4_.is_fairy;
   trace("isFairy: " + _loc2_);
   var _loc5_ = !_loc2_ ? _root.opStages : _root.fairyStages;
   var _loc7_;
   var _loc8_;
   var _loc9_;
   if(stg < _loc5_.length)
   {
      _root.p2selt = _loc5_[stg];
   }
   else if(stg == _root.totalstage)
   {
      _loc7_ = !_loc2_ ? _root.opBoss : _root.fairyBoss;
      _root.p2selt = getRandInArray(_loc7_);
   }
   else if(_loc4_.vs)
   {
      _loc8_ = _loc4_.vs;
      _root.p2selt = _loc8_[stg - _loc5_.length];
   }
   else
   {
      _loc9_ = !_loc2_ ? _root.fairyStages : _root.opStages;
      _root.p2selt = getRandInArray(_loc9_);
   }
   var _loc6_ = _root.getFighterData(_root.p2selt);
   if(_loc6_.map)
   {
      _root.curStage = _loc6_.map;
   }
   else
   {
      _root.curStage = _root.getRandMap();
   }
   stgObj = {};
   stgObj.stg = stg;
   stgObj.p2selt = _root.p2selt;
   stgObj.p2sf = _root.p2sf;
   stgObj.curStage = _root.curStage;
}
function onPassStg()
{
   _root.stage += 1;
   trace("onPassStg:" + _root.stage + "," + _root.totalstage);
   if(_root.stage >= _root.totalstage + 1)
   {
      _root.gotoAndStop("congratution");
      return undefined;
   }
   gostg(_root.stage);
}
function getRandInArray(a, remove, beside)
{
   trace("getRandInArray:" + a + "," + remove + "," + beside);
   var _loc2_ = Math.floor(Math.random() * a.length);
   var _loc3_ = a[_loc2_];
   if(beside != undefined && _loc3_ == beside)
   {
      return getRandInArray(a,remove,beside);
   }
   if(remove == true)
   {
      a.splice(_loc2_,1);
   }
   return _loc3_;
}
function getRandInObject(o)
{
   for(var _loc2_ in o)
   {
      return o[_loc2_];
      break;
   }
   return undefined;
}
function shine(color)
{
   if(isNaN(color))
   {
      color = 16777215;
   }
   _root.shinemc.gotoAndStop("colors");
   var _loc2_ = _root.shinemc.cmc;
   var _loc4_ = new Color(_loc2_);
   _loc4_.setRGB(color);
   _loc2_.gotoAndPlay(2);
}
function debug(txt)
{
   trace("debug : " + txt);
   var _loc2_ = _root.debugtxt;
   if(!_loc2_)
   {
      return undefined;
   }
   _loc2_.text += txt + "\n";
   if(_loc2_.bottomScroll > _loc2_.maxscroll)
   {
      _loc2_.scroll += _loc2_.maxscroll;
   }
}
function touchFloorEffect(selfmc)
{
   addChildXG(selfmc,"XG_hitfloor");
}
function array_indexOf(array, val)
{
   var _loc1_ = 0;
   while(_loc1_ < array.length)
   {
      if(array[_loc1_] == val)
      {
         return _loc1_;
      }
      _loc1_ = _loc1_ + 1;
   }
   return -1;
}
function showFace(pn, frame)
{
   var _loc2_ = _root.ts_face;
   _loc2_.frame = frame;
   _loc2_.gotoAndPlay("in");
}
function hideFace(pn)
{
   var _loc2_ = _root.ts_face;
   _loc2_.gotoAndPlay("out");
}
function bsd(pn, xg, fz)
{
   _root.zhanting = true;
   shine();
   if(xg == "XG_cbs")
   {
      blackStg("CBS");
   }
   else
   {
      blackStg();
   }
   if(pn != 1 && pn != 2)
   {
      return undefined;
   }
   var _loc5_ = pn != 1 ? 1 : 2;
   var _loc7_ = _root.game["p" + _loc5_];
   var _loc9_ = _root.game["p" + pn];
   var _loc6_ = _loc7_.mc;
   var _loc8_ = _loc9_.mc;
   var _loc3_ = _root.game["p" + _loc5_ + "fz"];
   var _loc10_ = _root.game["p" + pn + "fz"];
   if(!xg)
   {
      xg = "XG_bs";
   }
   if(fz)
   {
      _loc3_.bs = 1;
      stopMc(_loc6_);
      addChildXG(_loc3_,xg);
   }
   else
   {
      _loc6_.bs = 1;
      stopMc(_loc3_);
      addChildXG(_loc7_,xg);
   }
   stopMc(_loc8_);
   stopMc(_loc10_);
}
function stopMc(mc)
{
   if(mc.hited == 0 && mc.bs == 0)
   {
      mc.stop();
   }
}
function playMc(mc)
{
   if(mc.attacking === false)
   {
      return undefined;
   }
   if(mc.hited == 0)
   {
      mc.play();
   }
}
function bsw(pn, fz)
{
   var _loc2_ = pn != 1 ? 1 : 2;
   hideFace(pn);
   resumeBlackStg();
   var _loc9_ = _root.game["p" + _loc2_];
   var _loc7_ = _root.game["p" + pn];
   var _loc4_ = _loc9_.mc;
   var _loc6_ = _loc7_.mc;
   var _loc5_ = _root.game["p" + _loc2_ + "fz"];
   var _loc8_ = _root.game["p" + pn + "fz"];
   if(fz)
   {
      _loc5_.bs = 0;
      playMc(_loc4_);
   }
   else
   {
      _loc4_.bs = 0;
      playMc(_loc5_);
   }
   playMc(_loc6_);
   playMc(_loc8_);
   _root.zhanting = false;
}
function blackStg(frame)
{
   if(frame == undefined)
   {
      frame = 2;
   }
   _root.game.bgmc._visible = _root.game.fgmc._visible = false;
   _root.weathermc._visible = false;
   _root.blackMu.gotoAndStop(frame);
}
function resumeBlackStg()
{
   _root.game.bgmc._visible = _root.game.fgmc._visible = true;
   _root.weathermc._visible = true;
   _root.blackMu.gotoAndStop(1);
}
function cbsd(pn)
{
   bsd(pn,"XG_cbs");
   _root.焦点 = pn != 2 ? "p2" : "p1";
}
function cbsw(pn)
{
   _root.焦点 = "all";
   bsw(pn);
}
function BG_Black(isshow)
{
   if(isshow == true)
   {
      heimu._visible = true;
   }
   else
   {
      heimu._visible = false;
   }
}
function initGameStart()
{
   _root.xuntiaoInitlize();
}
function startGame()
{
   _root.chushi();
   _root.p2loaded = true;
   _root.stageSound.start(0,999);
   _root.stageSound.setVolume(50);
}
function fadinXuetiao()
{
   _root.xuetiao.gotoAndPlay("in");
}
function fadoutXuetiao()
{
   _root.xuetiao.gotoAndPlay("out");
}
function bdxg(selfmc)
{
   var _loc2_;
   var _loc3_;
   switch(selfmc.bdzl)
   {
      case 1:
         addChildXG(selfmc._parent,"XG_kan");
         break;
      case 2:
         addChildXG(selfmc._parent,"XG_qdj");
         break;
      case 3:
         addChildXG(selfmc._parent,"XG_qdjx");
         break;
      case 4:
         addChildXG(selfmc._parent,"XG_mfdj");
         break;
      case 5:
         addChildXG(selfmc._parent,"XG_mfdjx");
         break;
      case 6:
         addChildXG(selfmc._parent,"XG_kanx");
         break;
      case 7:
         selfmc._parent.setColor([{rb:255,gb:25,bb:-255},{rb:255,gb:86,bb:-255}]);
         addChildXG(selfmc._parent,"XG_fire");
         break;
      case 8:
         selfmc._parent.setColor([{rb:0,gb:153,bb:255},{rb:0,gb:198,bb:255}]);
         addChildXG(selfmc._parent,"XG_ice");
         break;
      case 9:
         selfmc._parent.setColor([{rb:71,gb:91,bb:255},{rb:178,gb:142,bb:255}]);
         addChildXG(selfmc._parent,"XG_leidian");
         break;
      case 10:
         _loc2_ = new Array();
         _loc2_ = _loc2_.concat([0.3086,0.6094,0.082,0,0]);
         _loc2_ = _loc2_.concat([0.3086,0.6094,0.082,0,0]);
         _loc2_ = _loc2_.concat([0.3086,0.6094,0.082,0,0]);
         _loc2_ = _loc2_.concat([0,0,0,1,0]);
         _loc3_ = new flash.filters.ColorMatrixFilter(_loc2_);
         selfmc.filters = [_loc3_];
         addChildXG(selfmc._parent,"XG_stone");
      default:
         return;
   }
}
function bdfyxg(selfmc)
{
   switch(selfmc.bdzl)
   {
      case 1:
         addChildXG(selfmc._parent,"XG_fykan");
         break;
      case 6:
         addChildXG(selfmc._parent,"XG_fykanx");
         break;
      case 2:
         addChildXG(selfmc._parent,"XG_fyq");
         break;
      case 3:
         addChildXG(selfmc._parent,"XG_fyqx");
         break;
      case 4:
      case 10:
         addChildXG(selfmc._parent,"XG_mffy");
         break;
      case 5:
      case 7:
      case 8:
      case 9:
         addChildXG(selfmc._parent,"XG_mffyx");
      default:
         return;
   }
}
function bdfyxg2(selfmc)
{
   switch(selfmc.bdzl)
   {
      case 1:
      case 2:
         addChildXG(selfmc._parent,"XG_fyq");
         break;
      case 3:
      case 6:
         addChildXG(selfmc._parent,"XG_fyqx");
         break;
      case 4:
      case 10:
         addChildXG(selfmc._parent,"XG_mffy");
         break;
      case 5:
      case 7:
      case 8:
      case 9:
         addChildXG(selfmc._parent,"XG_mffyx");
      default:
         return;
   }
}
function shunbuxg(player)
{
   addChildXG(player,"XG_rush");
}
function jumpxg(player)
{
   addChildXG(player,"XG_jump");
}
function luodixg(player)
{
   addChildXG(player,"XG_luodi");
}
function fzccXg(fz)
{
   addChildXG(fz,"XG_fzcc");
}
function addChildXG(playermc, xgclass)
{
   var _loc2_ = _root.game.layer_effect.getNextHighestDepth();
   _root.game.layer_effect.attachMovie(xgclass,"xgmc" + _loc2_,_loc2_);
   var _loc3_ = _root.game.layer_effect["xgmc" + _loc2_];
   _loc3_._x = playermc._x;
   _loc3_._y = playermc._y;
   _loc3_._xscale = playermc._xscale;
}
function KOplay(pn)
{
   var _loc2_ = pn != 1 ? "p1" : "p2";
   _root.焦点 = _loc2_;
   koPause = true;
   pauseGame();
   blackStg("KO");
   _root.KO.play();
}
function KOend()
{
   resumeBlackStg();
   _root.fadoutXuetiao();
   koPause = false;
   resumeGame();
}
function pauseGame()
{
   _root.zhanting = true;
   stopMc(_root.game.p1.mc);
   stopMc(_root.game.p2.mc);
   stopMc(_root.game.p1fz);
   stopMc(_root.game.p2fz);
}
function resumeGame()
{
   if(koPause)
   {
      return undefined;
   }
   _root.zhanting = false;
   playMc(_root.game.p1.mc);
   playMc(_root.game.p2.mc);
   playMc(_root.game.p1fz);
   playMc(_root.game.p2fz);
}
function shadowEffect(gid, param)
{
   var _loc3_ = _root.game[gid];
   var _loc5_ = _root.game.backeffect;
   if(!_loc5_)
   {
      return undefined;
   }
   debug("shadowEffect , " + gid + " , " + _loc5_);
   if(param == null)
   {
      param = {};
   }
   if(isNaN(param.alphaStart))
   {
      param.alphaStart = 100;
   }
   if(isNaN(param.alphaLose))
   {
      param.alphaLose = 10;
   }
   var _loc6_ = _loc5_.getNextHighestDepth();
   var _loc8_ = new flash.display.BitmapData(_loc3_._width,_loc3_._height,true,0);
   var _loc7_ = _loc3_.getBounds(_loc3_);
   var _loc9_ = new flash.geom.Matrix(1,0,0,1,- _loc7_.xMin,- _loc7_.yMin);
   _loc8_.draw(_loc3_,_loc9_,param.colorTransform);
   _loc5_.createEmptyMovieClip("mc" + _loc6_,_loc6_);
   var _loc4_ = _loc5_["mc" + _loc6_];
   debug("_child[mc" + _loc6_ + "] = " + _loc4_);
   _loc4_._xscale = _loc3_._xscale;
   _loc4_.attachBitmap(_loc8_,_loc6_);
   _loc4_._x = _loc3_._x + _loc7_.xMin * (_loc3_._xscale <= 0 ? -1 : 1);
   _loc4_._y = _loc3_._y + _loc7_.yMin;
   _loc4_._alpha = param.alphaStart;
   _loc4_.onEnterFrame = function()
   {
      this._alpha -= param.alphaLose;
      if(this._alpha <= 0)
      {
         this.removeMovieClip();
      }
   };
}
function getDayDiff(d1, d2)
{
   var _loc1_ = d1.getTime() - d2.getTime();
   return _loc1_ / 86400000;
}
function renderIng()
{
   shakeIng();
}
function shake(pow, holdFrame)
{
   if(pow == undefined)
   {
      pow = 6;
   }
   if(holdFrame == undefined)
   {
      holdFrame = 3;
   }
   _shakePow = pow;
   _shakeDis = pow / holdFrame * 2;
}
function shakeIng()
{
   if(_shakePow == 0)
   {
      return undefined;
   }
   trace("shakeIng " + _shakePow);
   _root._y += _shakePow;
   if(_shakePow < 0)
   {
      if(_shakePow > (- _shakeDis) * 2)
      {
         _shakePow = 0;
         _shakeDis = 0;
         _root._y = 0;
         return undefined;
      }
      _shakePow += _shakeDis;
   }
   _shakePow *= -1;
}
_root.clearint = function()
{
   clearInterval(_root.timeset);
   clearInterval(_root.xtset);
   clearInterval(_root.kcint);
   clearInterval(_root.nxtfht);
   clearInterval(_root.scrnset);
   clearInterval(_root.airanset);
   clearInterval(_root.feiint);
   clearInterval(_root.feiint2);
   clearInterval(_root.zdbxint);
};
_root.showKeyName = function(key)
{
   var _loc1_ = new Object();
   _loc1_[49] = "1";
   _loc1_[50] = "2";
   _loc1_[51] = "3";
   _loc1_[52] = "4";
   _loc1_[53] = "5";
   _loc1_[54] = "6";
   _loc1_[55] = "7";
   _loc1_[56] = "8";
   _loc1_[57] = "9";
   _loc1_[48] = "0";
   _loc1_[81] = "Q";
   _loc1_[87] = "W";
   _loc1_[69] = "E";
   _loc1_[82] = "R";
   _loc1_[84] = "T";
   _loc1_[89] = "Y";
   _loc1_[85] = "U";
   _loc1_[73] = "I";
   _loc1_[79] = "O";
   _loc1_[80] = "P";
   _loc1_[219] = "[";
   _loc1_[221] = "]";
   _loc1_[65] = "A";
   _loc1_[83] = "S";
   _loc1_[68] = "D";
   _loc1_[70] = "F";
   _loc1_[71] = "G";
   _loc1_[72] = "H";
   _loc1_[74] = "J";
   _loc1_[75] = "K";
   _loc1_[76] = "L";
   _loc1_[186] = ";";
   _loc1_[222] = "\'";
   _loc1_[90] = "Z";
   _loc1_[88] = "X";
   _loc1_[67] = "C";
   _loc1_[86] = "V";
   _loc1_[66] = "B";
   _loc1_[78] = "N";
   _loc1_[77] = "M";
   _loc1_[32] = "Space";
   _loc1_[38] = "↑";
   _loc1_[40] = "↓";
   _loc1_[37] = "←";
   _loc1_[39] = "→";
   _loc1_[45] = "Ins";
   _loc1_[36] = "Hom";
   _loc1_[33] = "PaU";
   _loc1_[46] = "Del";
   _loc1_[35] = "End";
   _loc1_[34] = "PaD";
   _loc1_[96] = "Num0";
   _loc1_[110] = "Num.";
   _loc1_[97] = "Num1";
   _loc1_[98] = "Num2";
   _loc1_[99] = "Num3";
   _loc1_[100] = "Num4";
   _loc1_[101] = "Num5";
   _loc1_[102] = "Num6";
   _loc1_[103] = "Num7";
   _loc1_[104] = "Num8";
   _loc1_[105] = "Num9";
   _loc1_[106] = "Num*";
   _loc1_[111] = "Num/";
   _loc1_[107] = "Num+";
   _loc1_[109] = "Num-";
   return _loc1_[key];
};
var chushi = function()
{
   if(_root.p1cpu == false)
   {
      _root.game.p1.mc.上 = _root.w;
      _root.game.p1.mc.下 = _root.s;
      _root.game.p1.mc.左 = _root.a;
      _root.game.p1.mc.右 = _root.d;
      _root.game.p1.mc.斩 = _root.j;
      _root.game.p1.mc.跳 = _root.k;
      _root.game.p1.mc.冲 = _root.l;
      _root.game.p1.mc.招 = _root.u;
      _root.game.p1.mc.必杀 = _root.i;
      _root.game.p1.mc.换 = _root.o;
   }
   if(_root.p2cpu == false)
   {
      _root.game.p2.mc.上 = _root.上箭;
      _root.game.p2.mc.下 = _root.下箭;
      _root.game.p2.mc.左 = _root.左箭;
      _root.game.p2.mc.右 = _root.右箭;
      _root.game.p2.mc.斩 = _root.N1;
      _root.game.p2.mc.跳 = _root.N2;
      _root.game.p2.mc.冲 = _root.N3;
      _root.game.p2.mc.招 = _root.N4;
      _root.game.p2.mc.必杀 = _root.N5;
      _root.game.p2.mc.换 = _root.N6;
   }
   _root.p1bs = _root.p1selt;
   _root.p2bs = _root.p2selt;
   _root.game.p1._x = 870;
   _root.game.p2._x = 1135;
   _root.game.p1._y = _root.game.p2._y = _root.floorY;
   _root.game.p1._xscale = 100;
   _root.game.p2._xscale = -100;
   _root.game.p1.mc.hp = _root.game.p2.mc.hp = _root.maxhp;
};
var koPause = false;
var _shakePow = 0;
var _shakeDis = 0;
