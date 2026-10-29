function checkSO()
{
   mySO = SharedObject.getLocal("bvn_5d");
   if(!mySO.flush(1))
   {
      System.showSettings(1);
   }
}
_root.w = 87;
_root.s = 83;
_root.a = 65;
_root.d = 68;
_root.j = 74;
_root.k = 75;
_root.l = 76;
_root.u = 85;
_root.i = 73;
_root.o = 79;
_root.yk = 89;
_root.nk = 78;
_root.上箭 = 38;
_root.下箭 = 40;
_root.左箭 = 37;
_root.右箭 = 39;
_root.N1 = 97;
_root.N2 = 98;
_root.N3 = 99;
_root.N4 = 100;
_root.N5 = 101;
_root.N6 = 102;
var txt = "";
var txt2 = "";
var txtst = 0;
var txtst2 = 0;
var p1ws = 1;
var p2ws = 1;
var wxs = false;
var modo = 1;
var maxhp = 1000;
var loop = 10;
var zhongli = 10;
var zhanting = false;
var gamePaused = false;
var ding = false;
var AI = 5;
var p1selt = "";
var p2selt = "";
var p1bs = "";
var p2bs = "";
var p1cpu = false;
var p2cpu = false;
var gametime = 60;
var maxtime = 60;
var to = false;
var qjplayed = 0;
var rounds = 1;
var 焦点 = "all";
var floorY = -25;
var p1ox = 320;
var p2ox = 650;
var p2oy = floorY;
var p2oy = floorY;
var curStage = "";
var readying = false;
var mapSizeX = 1000;
var fighterDir = "fighter/";
var musicDir = "music/";
var fzDir = "fighter/fz/";
var bossStage = "蓝染";
var mapWeather = {};
var stageSound = new Sound();
_root.p1sf = "";
_root.p2sf = "";
keysound1 = new Sound(_root);
keysound1.attachSound("keysound1.mp3");
keysound2 = new Sound(_root);
keysound2.attachSound("keysound2.mp3");
_root.stage = 0;
_root.totalstage = 7;
mySO = SharedObject.getLocal("bvn_5d");
checkSO();
mySO = SharedObject.getLocal("bvn_5d");
mySo.data.name = "bleachvsnaruto";
success = mySO.flush(100000);
if(success == "pending")
{
   mySO.onStatus = function(result)
   {
      if(result.code == "SharedObject.Flush.Success")
      {
         trace("Sucess writing to disk");
         writeSuccess = true;
      }
      else
      {
         trace("Failure writing to disk");
         writeSuccess = false;
      }
   };
}
else
{
   writeSuccess = success;
}
mySO = SharedObject.getLocal("bvn_5d");
if(mySO.data.w != undefined)
{
   _root.w = mySO.data.w;
   _root.s = mySO.data.s;
   _root.a = mySO.data.a;
   _root.d = mySO.data.d;
   _root.j = mySO.data.j;
   _root.k = mySO.data.k;
   _root.l = mySO.data.l;
   _root.u = mySO.data.u;
   _root.i = mySO.data.i;
   _root.o = mySO.data.o;
   _root.上箭 = mySO.data.上箭;
   _root.下箭 = mySO.data.下箭;
   _root.左箭 = mySO.data.左箭;
   _root.右箭 = mySO.data.右箭;
   _root.N1 = mySO.data.N1;
   _root.N2 = mySO.data.N2;
   _root.N3 = mySO.data.N3;
   _root.N4 = mySO.data.N4;
   _root.N5 = mySO.data.N5;
   _root.N6 = mySO.data.N6;
   _root.maxhp = mySO.data.maxhp;
   _root.AI = mySO.data.AI;
   _root.maxtime = mySO.data.maxtime;
   _root._quality = mySO.data.qualiy;
}
var cpurw = new Array();
var cpufz = new Array();
var narutoStages = ["露其雅","一护","恋次","日番谷","一护万解"];
var bleachStages = ["手鞠","鸣人","佐助","宁次","鸣人九尾"];
var bleachStageMaps = ["现世","尸魂界通道","流魂街","静涎亭","双极","尸魂界通道","静涎亭","现世"];
var narutoStageMaps = ["木叶村","温泉","火影瀑布","宇智波村","楼顶","木叶村","楼顶","火影瀑布"];
var bleachElseStages = ["白哉","银"];
var narutoElseStages = ["小李","鼬"];
_root.totalstage = 7;
trace("_root.totalstage" + _root.totalstage);
