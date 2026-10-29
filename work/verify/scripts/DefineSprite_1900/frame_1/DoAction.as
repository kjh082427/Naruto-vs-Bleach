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
function loadSound()
{
   var _loc3_ = _root.getFighterData(_root.p2selt);
   var _loc2_;
   if(_loc3_.music)
   {
      if(Math.random() < 0.8)
      {
         _loc2_ = _loc3_.music;
      }
   }
   var _loc4_;
   if(!_loc2_)
   {
      if(Math.random() < 0.5)
      {
         _loc2_ = !_loc3_.isNaruto ? _root.bleachMusic : _root.narutoMusic;
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
   _root.stageSound.onLoad = function(succ)
   {
      if(!succ)
      {
         _root.debug("sound load fail!");
         _this.play();
      }
   };
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
   trace("loadman : " + pr + "," + _root[pr + "selt"]);
   var _loc3_ = _root.getFighterData(_root[pr + "selt"]);
   _this._loader.loadClip(_root.fighterDir + _loc3_.url,_root.game[pr]);
}
function loadfz(pr)
{
   trace("loadfz:" + pr + "," + _root[pr + "sf"]);
   var _loc3_ = _root.getFighterData(_root[pr + "sf"]);
   _this._loader.loadClip(_root.fzDir + _loc3_.fzurl,_root.game[pr + "fz"]);
}
stop();
var loadComplete;
var playComplete;
var _this = this;
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
   loadfz("p1");
},function()
{
   loadfz("p2");
},function()
{
   loadSound();
}];
var loadStep = 0;
var _loader = new MovieClipLoader();
var LO = new Object();
LO.onLoadProgress = function(target, bytesLoaded, bytesTotal)
{
   coutProcess(bytesLoaded / bytesTotal);
};
LO.onLoadError = loadError;
LO.onLoadComplete = function(target)
{
   loadStep++;
   loadSteps[loadStep]();
};
_loader.addListener(LO);
loadSteps[loadStep]();
