function startGame()
{
   trace("startGame " + loadComplete + " " + playComplete);
   if(loadComplete)
   {
      _parent.gotoAndPlay("skip");
   }
   else
   {
      playComplete = true;
   }
}
function loadError(target_mc, errorCode)
{
   trace("加载错误 : \nErrorCode:" + errorCode);
}
function coutProcess(p)
{
   lbar._xscale = Math.round((p + loadStep) / loadSteps.length * 100);
   if(lbar._xscale >= 100)
   {
      delete lbar.onEnterFrame;
      _this.play();
   }
}
function loadNext()
{
   loadStep++;
   loadSteps[loadStep]();
}
function loadSound()
{
   var _loc2_;
   if(p2obj.music)
   {
      if(Math.random() < 0.8)
      {
         _loc2_ = p2obj.music;
      }
   }
   var _loc3_;
   var _loc4_;
   if(!_loc2_)
   {
      if(Math.random() < 0.5)
      {
         _loc3_ = !p2obj.is_fairy ? _root.opMusic : _root.fairyMusic;
         _loc2_ = _root.getRandInArray(_loc3_);
      }
      else if(_root.weather == "大雨" || _root.weather == "雷雨")
      {
         _loc2_ = _root.rainMusic;
      }
      else
      {
         _loc4_ = _root.getMapData(_root.curStage);
         _loc2_ = _loc4_.music;
      }
   }
   if(!_loc2_)
   {
      _root.debug("sound is null!");
      _this.play();
      return undefined;
   }
   var loadInt;
   _root.stageSound = new Sound();
   _root.stageSound.loadSound(_root.musicDir + _loc2_);
   _root.debug("loadSound : " + _root.musicDir + _loc2_);
   lbar.onEnterFrame = function()
   {
      _root.debug(_root.stageSound.getBytesLoaded() + " , " + _root.stageSound.getBytesTotal());
      if(_root.stageSound.getBytesLoaded() == 0)
      {
         loadInt++;
         if(loadInt > 300)
         {
            _this.play();
         }
      }
      coutProcess(_root.stageSound.getBytesLoaded() / _root.stageSound.getBytesTotal());
   };
}
function loadman(pr)
{
   _root.debug("loadman : " + pr);
   var _loc6_ = _this[pr + "obj"].url;
   var mc = _root.game[pr];
   var _loc3_ = _root.fighterDir + _loc6_;
   loadMovie(_loc3_,mc);
   _this.onEnterFrame = function()
   {
      var _loc3_ = mc.getBytesLoaded();
      var _loc2_ = mc.getBytesTotal();
      _root.debug(pr + " : " + _loc3_ + "/" + _loc2_);
      if(_loc2_ < 1024)
      {
         return undefined;
      }
      var _loc4_ = _loc3_ / _loc2_;
      coutProcess(_loc4_);
      if(_loc4_ >= 1)
      {
         delete _this.onEnterFrame;
         loadNext();
      }
   };
}
var mapobj = _root.getMapData(_root.curStage);
trace(mapobj + ";" + _root.curStage);
_root.weather = _root.getRandInArray(mapobj.weather);
stop();
var loadComplete;
var playComplete;
var _this = this;
var p1obj = _root.getFighterData(_root.p1selt);
var p2obj = _root.getFighterData(_root.p2selt);
loadComplete = playComplete = false;
error._visible = false;
lbar._xscale = 1;
var loadSteps = [function()
{
   loadman("p1");
},function()
{
   loadman("p2");
},function()
{
   loadSound();
}];
var loadStep = 0;
loadSteps[loadStep]();
