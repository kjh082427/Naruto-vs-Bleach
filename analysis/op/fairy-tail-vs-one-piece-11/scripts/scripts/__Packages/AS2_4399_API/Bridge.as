class AS2_4399_API.Bridge
{
   var _4399_ad_id;
   var _addItemsCallBackFunc;
   var _buyCallBackFunc;
   var _clearItemsCallBackFunc;
   var _closePanelCallBackFunc;
   var _decMoneyInsCallBackFunc;
   var _delItemCallBackFunc;
   var _getBalanceCallBackFunc;
   var _getBalanceInsCallBackFunc;
   var _getDataCallBackFunc;
   var _getFreePacCallBackFunc;
   var _getIsLogCallBackFunc;
   var _getListCallBackFunc;
   var _getPackageCallBackFunc;
   var _getPaiedMoneyCallBackFunc;
   var _getPayPacCallBackFunc;
   var _getRechargedMoneyCallBackFunc;
   var _getSaveUiIdxCallBackFunc;
   var _getServerTimeCallBackFunc;
   var _getStoreStateCallBackFunc;
   var _incMoneyInsCallBackFunc;
   var _logOutCallBackFunc;
   var _loginCallBackFunc;
   var _modifyExCallBackFunc;
   var _multipleErrorCallBackFunc;
   var _netGetErrorCallBackFunc;
   var _netSaveErrorCallBackFunc;
   var _noticeSetExFlagCallBackFunc;
   var _noticeTypeCallBackFunc;
   var _packageErrorCallBackFunc;
   var _payErrorInsCallBackFunc;
   var _payMoneyInsCallBackFunc;
   var _rankListErrorCallBackFunc;
   var _rankListSuccessCallBackFunc;
   var _restartGameCallBackFunc;
   var _saveDataCallBackFunc;
   var _updateItemCallBackFunc;
   var _usePayApiCallBackFunc;
   var b3c3d29f19dae588;
   var oldHitTest;
   static var eb7560c4326bb0e1;
   var bfc9efbc39790568 = 0;
   var ea9e2aece3ec241a = 1000;
   var bf443b797ef8a66b = 20;
   static var _instance = null;
   var c75362407e1d1b80 = false;
   var joinDataObj = new Object();
   function Bridge()
   {
      if(!eb7560c4326bb0e1)
      {
         throw new Error("创建出错,请使用getInstance()方法创建!!!!");
      }
      this._4399_ad_id = "92d6cef76cd06829e088932fe9fd819b";
      _root.focusManager.enabled = false;
      this.b3c3d29f19dae588 = true;
      this[a5ce41e255a608030c([101,98,49,98,52,54,99,56,48,49,48,97,97,53,97,100])] = _root[a5ce41e255a608030c([95,117,114,108])];
      _global[a5ce41e255a608030c([97,57,56,100,50,102,100,57,57,99,48,50,101,56,53,54])] = a5ce41e255a608030c([115,97,118,101,80,114,111,99,101,115,115,70,117,110,99]);
      this[a5ce41e255a608030c([102,98,100,55,100,97,55,54,57,99,57,50,98,97,49,48])] = this[a5ce41e255a608030c([100,54,52,50,51,55,101,102,99,49,54,98,53,48,56,55])];
      this[a5ce41e255a608030c([100,48,102,97,98,51,55,51,50,97,53,99,98,99,100,49])] = _global[a5ce41e255a608030c([78,97,78])];
      _root[a5ce41e255a608030c([95,108,111,99,107,114,111,111,116])] = true;
      this.movieClipTest();
      System.security[a5ce41e255a608030c([97,108,108,111,119,68,111,109,97,105,110])]("*");
      System.security[a5ce41e255a608030c([97,108,108,111,119,73,110,115,101,99,117,114,101,68,111,109,97,105,110])]("*");
      this[a5ce41e255a608030c([97,97,51,102,102,97,102,49,52,57,98,51,53,49,102,54])]();
   }
   static function getInstance()
   {
      eb7560c4326bb0e1 = true;
      if(_instance == null)
      {
         _instance = new AS2_4399_API.Bridge();
      }
      eb7560c4326bb0e1 = false;
      return _instance;
   }
   function userLogOut(callBackContext, callBackFunc)
   {
      this._logOutCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([117,115,101,114,76,111,103,79,117,116]),param:null});
   }
   function restartGame(callBackContext, callBackFunc)
   {
      this._restartGameCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function getServerTime(callBackContext, callBackFunc)
   {
      this._getServerTimeCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,83,101,114,118,101,114,84,105,109,101]),param:null});
   }
   function noticeUserLogOut(callBackContext, callBackFunc)
   {
      this._logOutCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function changeScore(curScore)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([99,104,97,110,103,101,83,99,111,114,101]),param:curScore});
   }
   function submitScore(totalScore)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,117,98,109,105,116,83,99,111,114,101]),param:totalScore});
   }
   function showShopUi()
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,104,111,119,83,104,111,112,85,105]),param:null});
   }
   function consumeItemFun(proId, callBackContext, callBackFunc, errorBackFunc)
   {
      this._delItemCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([99,111,110,115,117,109,101,73,116,101,109,70,117,110]),param:[proId]});
   }
   function clearItemsByExTypeFun(callBackContext, callBackFunc, errorBackFunc, type, exFlag, sn)
   {
      this._clearItemsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([99,108,101,97,114,73,116,101,109,115,66,121,69,120,84,121,112,101,70,117,110]),param:[type,exFlag,sn]});
   }
   function getPackageInfoFun(callBackContext, callBackFunc, errorBackFunc, pageNum, curPage, typeId, exFlag, sn)
   {
      this._getPackageCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(isNaN(pageNum) || pageNum == undefined)
      {
         pageNum = 10;
      }
      if(isNaN(curPage) || curPage == undefined)
      {
         curPage = 1;
      }
      if(typeId == undefined || typeId == "")
      {
         typeId = "0";
      }
      if(exFlag == undefined)
      {
         exFlag = null;
      }
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,80,97,99,107,97,103,101,73,110,102,111,70,117,110]),param:[pageNum,curPage,typeId,exFlag,sn]});
   }
   function getShopItemsFun(idsAry, callBackContext, callBackFunc, errorBackFunc, sn)
   {
      this._getPackageCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,83,104,111,112,73,116,101,109,115,70,117,110]),param:[idsAry,sn]});
   }
   function getNoticeTypeFun(callBackContext, callBackFunc, errorBackFunc)
   {
      this._noticeTypeCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
   }
   function getPayPacInfoFun(callBackContext, callBackFunc, errorBackFunc, pageNum, curPage, typeId)
   {
      this._getPayPacCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(isNaN(pageNum) || pageNum == undefined)
      {
         pageNum = 8;
      }
      if(isNaN(curPage) || curPage == undefined)
      {
         curPage = 1;
      }
      if(typeId == undefined || typeId == "")
      {
         typeId = "0";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,80,97,121,80,97,99,73,110,102,111,70,117,110]),param:[pageNum,curPage,typeId]});
   }
   function buyProFun(proId, count, callBackContext, callBackFunc, errorBackFunc, sn)
   {
      this._buyCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([98,117,121,80,114,111,70,117,110]),param:[proId,count,sn]});
   }
   function getFreePacInfoFun(callBackContext, callBackFunc, errorBackFunc, pageNum, curPage, typeId)
   {
      this._getFreePacCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(isNaN(pageNum) || pageNum == undefined)
      {
         pageNum = 0;
      }
      if(isNaN(curPage) || curPage == undefined)
      {
         curPage = 1;
      }
      if(typeId == undefined || typeId == "")
      {
         typeId = "0";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,70,114,101,101,80,97,99,73,110,102,111,70,117,110]),param:[pageNum,curPage,typeId]});
   }
   function removeItemsFun(dataAry, callBackContext, callBackFunc, errorBackFunc, sn)
   {
      this._delItemCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([114,101,109,111,118,101,73,116,101,109,115,70,117,110]),param:[dataAry,sn]});
   }
   function addItemsFun(dataAry, callBackContext, callBackFunc, errorBackFunc, sn)
   {
      this._addItemsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([97,100,100,73,116,101,109,115,70,117,110]),param:[dataAry,sn]});
   }
   function updateItemProFun(dataObj, callBackContext, callBackFunc, errorBackFunc, sn)
   {
      this._updateItemCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([117,112,100,97,116,101,73,116,101,109,80,114,111,70,117,110]),param:[dataObj,sn]});
   }
   function modifyExFun(callBackContext, callBackFunc, errorBackFunc, pId, exAry, sn)
   {
      this._modifyExCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._packageErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      if(sn == undefined)
      {
         sn = "";
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([109,111,100,105,102,121,69,120,70,117,110]),param:[pId,exAry,sn]});
   }
   function setExFlagFun(dataAry)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,101,116,69,120,70,108,97,103,70,117,110]),param:dataAry});
   }
   function noticeSetExFlagFun(callBackContext, callBackFunc)
   {
      this._noticeSetExFlagCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function getShopBalance(callBackContext, callBackFunc)
   {
      this._getBalanceCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function showGameList()
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,104,111,119,71,97,109,101,76,105,115,116]),param:null});
   }
   function showRefer(score)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([111,112,101,110,73,110,116,101,103,114,97,108,87,105,110]),param:[score]});
   }
   function showSort()
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([111,112,101,110,83,111,114,116,87,105,110]),param:null});
   }
   function usePayApi(callBackContext, callBackFunc)
   {
      this._usePayApiCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function incMoney(payMoneyVar, callBackContext, callBackFunc, errorBackFunc)
   {
      var _loc3_;
      if(payMoneyVar == null || payMoneyVar.money == undefined || isNaN(Number(payMoneyVar.money)))
      {
         _loc3_ = 0;
      }
      else
      {
         _loc3_ = Number(payMoneyVar.money);
      }
      this._incMoneyInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._payErrorInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([105,110,99,77,111,110,101,121]),param:[_loc3_]});
   }
   function decMoney(payMoneyVar, callBackContext, callBackFunc, errorBackFunc)
   {
      var _loc3_;
      if(payMoneyVar == null || payMoneyVar.money == undefined || isNaN(Number(payMoneyVar.money)))
      {
         _loc3_ = 0;
      }
      else
      {
         _loc3_ = Number(payMoneyVar.money);
      }
      this._decMoneyInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._payErrorInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([100,101,99,77,111,110,101,121]),param:[_loc3_]});
   }
   function getBalance(callBackContext, callBackFunc, errorBackFunc)
   {
      this._getBalanceInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._payErrorInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,66,97,108,97,110,99,101]),param:null});
   }
   function payMoney(payMoneyVar, callBackContext, callBackFunc, errorBackFunc)
   {
      var _loc3_;
      if(payMoneyVar == null || payMoneyVar.money == undefined || isNaN(Number(payMoneyVar.money)))
      {
         _loc3_ = 0;
      }
      else
      {
         _loc3_ = Number(payMoneyVar.money);
      }
      this._payMoneyInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._payErrorInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([112,97,121,77,111,110,101,121]),param:[_loc3_]});
   }
   function getTotalPaiedFun(callBackContext, callBackFunc, errorBackFunc, dateObj)
   {
      this._getPaiedMoneyCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._payErrorInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([112,97,105,101,100,77,111,110,101,121]),param:dateObj});
   }
   function getTotalRechargedFun(callBackContext, callBackFunc, errorBackFunc, dateObj)
   {
      this._getRechargedMoneyCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this._payErrorInsCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,errorBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([114,101,99,104,97,114,103,101,100,77,111,110,101,121]),param:dateObj});
   }
   function saveData(title, data, callBackContext, callBackFunc, ui, index)
   {
      if(ui == null || ui == undefined)
      {
         ui = true;
      }
      if(isNaN(index) || index == null || index == undefined)
      {
         index = 0;
      }
      this._saveDataCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      var _loc6_ = "";
      try
      {
         _loc6_ = AS2_4399_API.JSON.stringify(data);
      }
      catch(ex)
      {
         _loc6_ = "";
      }
      var _loc5_;
      var _loc4_;
      var _loc2_;
      var _loc3_;
      if(_loc6_.length > 15000)
      {
         _loc5_ = false;
         _loc4_ = Math.ceil(_loc6_.length / 15000);
         _loc2_ = 0;
         while(_loc2_ < _loc4_)
         {
            _loc3_ = _loc6_.substr(_loc2_ * 15000,15000);
            if(_loc2_ == _loc4_ - 1)
            {
               _loc5_ = true;
            }
            this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([106,111,105,110,68,97,116,97,70,117,110]),param:[title,_loc3_,ui,index,_loc5_]});
            _loc2_ = _loc2_ + 1;
         }
         return undefined;
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,97,118,101,68,97,116,97]),param:[title,data,ui,index]});
   }
   function getData(callBackContext, callBackFunc, ui, index)
   {
      if(ui == null || ui == undefined)
      {
         ui = true;
      }
      if(isNaN(index) || index == null || index == undefined)
      {
         index = 0;
      }
      this._getDataCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,68,97,116,97]),param:[ui,index]});
   }
   function openSaveUI(title, data, saveContext, saveFunc, getContext, getFunc)
   {
      this._getDataCallBackFunc = AS2_4399_API.Delegate.create(getContext,getFunc);
      this._saveDataCallBackFunc = AS2_4399_API.Delegate.create(saveContext,saveFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,76,105,115,116]),param:[title,data]});
   }
   function getSaveUiIdx(callBackContext, callBackFunc)
   {
      this._getSaveUiIdxCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function netSaveErrorCallBack(callBackContext, callBackFunc)
   {
      this._netSaveErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function netGetErrorCallBack(callBackContext, callBackFunc)
   {
      this._netGetErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function multipleErrorCallBack(callBackContext, callBackFunc)
   {
      this._multipleErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function getStoreState(callBackContext, callBackFunc)
   {
      this._getStoreStateCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,83,116,111,114,101,83,116,97,116,101]),param:null});
   }
   function getListData(callBackContext, callBackFunc)
   {
      this._getListCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,76,105,115,116,68,97,116,97]),param:null});
   }
   function getOneRankInfo(rankListId, uname)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,79,110,101,82,97,110,107,73,110,102,111]),param:[rankListId,uname]});
   }
   function getRankListByOwn(rankListId, idx, rankNum)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,82,97,110,107,76,105,115,116,66,121,79,119,110]),param:[rankListId,idx,rankNum]});
   }
   function getRankListsData(rankListId, pageSize, pageNum)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,82,97,110,107,76,105,115,116,115,68,97,116,97]),param:[rankListId,pageSize,pageNum]});
   }
   function submitScoreToRankLists(idx, rankInfoAry)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,117,98,109,105,116,83,99,111,114,101,84,111,82,97,110,107,76,105,115,116,115]),param:[idx,rankInfoAry]});
   }
   function getUserData(uid, idx)
   {
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([103,101,116,85,115,101,114,68,97,116,97]),param:[uid,idx]});
   }
   function rankListError(callBackContext, callBackFunc)
   {
      this._rankListErrorCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function rankListSuccess(callBackContext, callBackFunc)
   {
      this._rankListSuccessCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function setLogInCallBack(callBackContext, callBackFunc)
   {
      this._loginCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function testCtrl()
   {
   }
   function showLogPanel()
   {
      this.c75362407e1d1b80 = true;
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,104,111,119,76,111,103,80,97,110,101,108]),param:null});
   }
   function getIsLog(callBackContext, callBackFunc)
   {
      this._getIsLogCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([105,115,76,111,103]),param:null});
   }
   function setMouseVisible(bol)
   {
      this[a5ce41e255a608030c([98,51,99,51,100,50,57,102,49,57,100,97,101,53,56,56])] = bol;
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,101,116,77,111,117,115,101,86,105,115,105,98,108,101]),param:bol});
   }
   function d64237efc16b5087(_this)
   {
      if(this[a5ce41e255a608030c([101,52,100,51,99,56,100,97,101,51,48,97,102,53,53,57])])
      {
         return undefined;
      }
      var _loc3_;
      if(_global[a5ce41e255a608030c([105,115,78,97,78])](this[a5ce41e255a608030c([100,48,102,97,98,51,55,51,50,97,53,99,98,99,100,49])]))
      {
         _loc3_ = int(Math.random() * (this[a5ce41e255a608030c([101,98,49,98,52,54,99,56,48,49,48,97,97,53,97,100])].length - 1));
         this[a5ce41e255a608030c([100,48,102,97,98,51,55,51,50,97,53,99,98,99,100,49])] = _global[a5ce41e255a608030c([115,101,116,73,110,116,101,114,118,97,108])](this[a5ce41e255a608030c([101,98,54,101,49,50,102,102,54,52,53,56,51,51,99,55])],10000,this);
         this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([116,101,115,116,67,116,114,108]),param:_loc3_});
      }
   }
   function fed9cd2755d7cec4(_this)
   {
      if(_this[a5ce41e255a608030c([97,49,50,98,49,51,51,98,56,102,98,101,49,55,53,100])])
      {
         return undefined;
      }
      _this[a5ce41e255a608030c([102,98,100,55,100,97,55,54,57,99,57,50,98,97,49,48])](_this);
   }
   function testReturn(ab608cc046f2a6e6)
   {
   }
   function f8f09b15319aa987()
   {
   }
   function eb6e12ff645833c7(_this)
   {
      this[a5ce41e255a608030c([101,52,100,51,99,56,100,97,101,51,48,97,102,53,53,57])] = true;
      _global[a5ce41e255a608030c([99,108,101,97,114,73,110,116,101,114,118,97,108])](_this[a5ce41e255a608030c([100,48,102,97,98,51,55,51,50,97,53,99,98,99,100,49])]);
      this[a5ce41e255a608030c([100,48,102,97,98,51,55,51,50,97,53,99,98,99,100,49])] = _global[a5ce41e255a608030c([78,97,78])];
      _global[a5ce41e255a608030c([99,108,101,97,114,73,110,116,101,114,118,97,108])](_this.e6da1a6af0171de);
      _this.e6da1a6af0171de = _global[a5ce41e255a608030c([78,97,78])];
      _this[a5ce41e255a608030c([102,98,100,55,100,97,55,54,57,99,57,50,98,97,49,48])] = _this[a5ce41e255a608030c([102,56,102,48,57,98,49,53,51,49,57,97,97,57,56,55])];
      _this[a5ce41e255a608030c([100,98,102,53,48,51,55,51,57,53,98,99,54,48,54,101])](_this);
   }
   function dbf5037395bc606e(_this)
   {
      if(!_global[a5ce41e255a608030c([105,115,78,97,78])](_this[a5ce41e255a608030c([99,52,99,55,97,57,54,100,99,102,98,56,102,101,99,97])]))
      {
         return undefined;
      }
      if(!_global[a5ce41e255a608030c([105,115,78,97,78])](_this[a5ce41e255a608030c([98,49,56,55,99,48,50,100,98,53,52,52,98,54,52,100])]))
      {
         _global[a5ce41e255a608030c([99,108,101,97,114,73,110,116,101,114,118,97,108])](_this[a5ce41e255a608030c([98,49,56,55,99,48,50,100,98,53,52,52,98,54,52,100])]);
         _this[a5ce41e255a608030c([98,49,56,55,99,48,50,100,98,53,52,52,98,54,52,100])] = _global[a5ce41e255a608030c([78,97,78])];
      }
      if(_global[a5ce41e255a608030c([105,115,78,97,78])](_this[a5ce41e255a608030c([99,52,99,55,97,57,54,100,99,102,98,56,102,101,99,97])]))
      {
         _global[a5ce41e255a608030c([115,100,97,115,100,102,97])][a5ce41e255a608030c([95,118,105,115,105,98,108,101])] = false;
         _this[a5ce41e255a608030c([99,52,99,55,97,57,54,100,99,102,98,56,102,101,99,97])] = _global[a5ce41e255a608030c([115,101,116,73,110,116,101,114,118,97,108])](_this[a5ce41e255a608030c([101,50,50,99,48,51,101,48,48,54,54,99,50,101,55,50])],120000,_this);
      }
   }
   function e22c03e0066c2e72(_this)
   {
      if(!_global[a5ce41e255a608030c([105,115,78,97,78])](_this[a5ce41e255a608030c([99,52,99,55,97,57,54,100,99,102,98,56,102,101,99,97])]))
      {
         _global[a5ce41e255a608030c([99,108,101,97,114,73,110,116,101,114,118,97,108])](_this[a5ce41e255a608030c([99,52,99,55,97,57,54,100,99,102,98,56,102,101,99,97])]);
         _this[a5ce41e255a608030c([99,52,99,55,97,57,54,100,99,102,98,56,102,101,99,97])] = _global[a5ce41e255a608030c([78,97,78])];
      }
      _this[a5ce41e255a608030c([99,97,101,52,54,50,99,48,101,98,99,98,55,49,101,101])] = false;
      _this[a5ce41e255a608030c([98,51,97,50,55,54,49,100,53,97,52,102,55,97,100,98])](_this);
      _this[a5ce41e255a608030c([98,49,56,55,99,48,50,100,98,53,52,52,98,54,52,100])] = _global[a5ce41e255a608030c([115,101,116,73,110,116,101,114,118,97,108])](_this[a5ce41e255a608030c([100,98,102,53,48,51,55,51,57,53,98,99,54,48,54,101])],10000,_this);
   }
   function movieClipTest()
   {
      if(_level0 === undefined && MovieClip.prototype.oldHitTest === undefined)
      {
         var realRootForReal = _root;
         MovieClip.prototype.oldHitTest = MovieClip.prototype.hitTest;
         MovieClip.prototype.hitTest = function(x, y, shapeflag)
         {
            if(arguments.length === 1)
            {
               return this.oldHitTest(x);
            }
            var _loc3_ = {x:x,y:y};
            realRootForReal.localToGlobal(_loc3_);
            return this.oldHitTest(_loc3_.x,_loc3_.y,shapeflag);
         };
      }
   }
   function aa3ffaf149b351f6()
   {
      this[a5ce41e255a608030c([99,51,55,56,54,52,102,102,52,52,55,57,101,51,52,98])] = true;
      this[a5ce41e255a608030c([99,101,52,99,57,102,52,50,101,50,102,102,97,97,54,51])]();
   }
   function ce4c9f42e2ffaa63()
   {
      if(!_global[a5ce41e255a608030c([105,115,78,97,78])](this[a5ce41e255a608030c([101,54,51,99,50,57,48,52,53,99,56,97,50,55,53,102])]))
      {
         _global[a5ce41e255a608030c([99,108,101,97,114,73,110,116,101,114,118,97,108])](this[a5ce41e255a608030c([101,54,51,99,50,57,48,52,53,99,56,97,50,55,53,102])]);
      }
      this[a5ce41e255a608030c([101,54,51,99,50,57,48,52,53,99,56,97,50,55,53,102])] = _global[a5ce41e255a608030c([115,101,116,73,110,116,101,114,118,97,108])](this[a5ce41e255a608030c([102,48,57,97,102,50,97,52,101,102,51,53,54,53,54,56])],20,this);
   }
   function f09af2a4ef356568(d75659655174056e, func)
   {
      if(d75659655174056e[a5ce41e255a608030c([98,102,99,57,101,102,98,99,51,57,55,57,48,53,54,56])] >= d75659655174056e.ea9e2aece3ec241a)
      {
         d75659655174056e[a5ce41e255a608030c([99,51,55,56,54,52,102,102,52,52,55,57,101,51,52,98])] = false;
         _global[a5ce41e255a608030c([99,108,101,97,114,73,110,116,101,114,118,97,108])](d75659655174056e[a5ce41e255a608030c([101,54,51,99,50,57,48,52,53,99,56,97,50,55,53,102])]);
         d75659655174056e[a5ce41e255a608030c([101,54,51,99,50,57,48,52,53,99,56,97,50,55,53,102])] = _global[a5ce41e255a608030c([78,97,78])];
      }
      d75659655174056e[a5ce41e255a608030c([98,102,99,57,101,102,98,99,51,57,55,57,48,53,54,56])]++;
      if(_root[a5ce41e255a608030c([111,112,97,113,117,101,66,97,99,107,103,114,111,117,110,100])] != undefined)
      {
         d75659655174056e[a5ce41e255a608030c([101,100,99,97,102,49,51,100,98,97,51,98,50,102,50,99])](_root[a5ce41e255a608030c([111,112,97,113,117,101,66,97,99,107,103,114,111,117,110,100])]);
         _root[a5ce41e255a608030c([111,112,97,113,117,101,66,97,99,107,103,114,111,117,110,100])] = undefined;
         _global[a5ce41e255a608030c([99,108,101,97,114,73,110,116,101,114,118,97,108])](d75659655174056e[a5ce41e255a608030c([101,54,51,99,50,57,48,52,53,99,56,97,50,55,53,102])]);
         d75659655174056e[a5ce41e255a608030c([101,54,51,99,50,57,48,52,53,99,56,97,50,55,53,102])] = _global[a5ce41e255a608030c([78,97,78])];
         d75659655174056e[a5ce41e255a608030c([101,49,48,53,53,54,49,50,53,98,57,57,57,101,52,52])] = true;
         d75659655174056e[a5ce41e255a608030c([99,51,55,56,54,52,102,102,52,52,55,57,101,51,52,98])] = false;
      }
   }
   function edcaf13dba3b2f2c(a89bc777c9e57736)
   {
      this[a5ce41e255a608030c([97,102,52,48,53,49,102,102,55,50,49,57,97,48,56,56])] = a5ce41e255a608030c([65,83,51,95,52,51,57,57]) + a89bc777c9e57736;
      this[a5ce41e255a608030c([102,57,54,53,49,51,49,52,57,48,100,51,52,98,51,101])] = a5ce41e255a608030c([65,83,50,95,52,51,57,57]) + a89bc777c9e57736;
      if(this[a5ce41e255a608030c([97,48,56,49,102,49,48,55,56,99,51,52,56,53,55,98])] == null)
      {
         this[a5ce41e255a608030c([97,48,56,49,102,49,48,55,56,99,51,52,56,53,55,98])] = new LocalConnection();
      }
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([115,101,116,77,111,117,115,101,86,105,115,105,98,108,101]),param:this.b3c3d29f19dae588});
      this[a5ce41e255a608030c([97,48,56,49,102,49,48,55,56,99,51,52,56,53,55,98])][a5ce41e255a608030c([99,111,110,110,101,99,116])](this[a5ce41e255a608030c([102,57,54,53,49,51,49,52,57,48,100,51,52,98,51,101])]);
      this[a5ce41e255a608030c([97,48,56,49,102,49,48,55,56,99,51,52,56,53,55,98])][a5ce41e255a608030c([114,101,99,101,105,118,101,72,97,110,100,108,101,114])] = AS2_4399_API.Delegate.create(this,this[a5ce41e255a608030c([100,56,99,49,97,98,97,53,99,51,56,100,48,54,50,51])]);
      this[a5ce41e255a608030c([100,51,53,49,54,100,57,99,56,55,49,50,52,98,100,52])]({func:a5ce41e255a608030c([99,111,110,110,101,99,116]),param:null});
   }
   function d8c1aba5c38d0623(obj)
   {
      if(obj != null && obj.func != null)
      {
         switch(obj.func)
         {
            case a5ce41e255a608030c([117,115,101,114,76,111,103,105,110,79,117,116]):
               this._logOutCallBackFunc();
               return;
            case a5ce41e255a608030c([99,108,111,115,101,80,97,110,101,108]):
               this[a5ce41e255a608030c([99,108,111,115,101,80,97,110,101,108,70,117,110])](obj.param);
               return;
            case _global[a5ce41e255a608030c([97,57,56,100,50,102,100,57,57,99,48,50,101,56,53,54])]:
               this[a5ce41e255a608030c([115,97,118,101,80,114,111,99,101,115,115,70,117,110,99])](obj.param[0],obj.param[1]);
               return;
            case a5ce41e255a608030c([112,97,121,80,114,111,99,101,115,115,70,117,110,99]):
               this[a5ce41e255a608030c([112,97,121,80,114,111,99,101,115,115,70,117,110,99])](obj.param[0],obj.param[1]);
               return;
            case a5ce41e255a608030c([115,104,111,112,80,114,111,99,101,115,115,70,117,110,99]):
               this[a5ce41e255a608030c([115,104,111,112,80,114,111,99,101,115,115,70,117,110,99])](obj.param[0],obj.param[1]);
               return;
            case a5ce41e255a608030c([114,97,110,107,76,105,115,116,80,114,111,99,101,115,115,70,117,110,99]):
               this[a5ce41e255a608030c([114,97,110,107,76,105,115,116,80,114,111,99,101,115,115,70,117,110,99])](obj.param[0],obj.param[1]);
               return;
            case a5ce41e255a608030c([111,116,104,101,114,80,114,111,99,101,115,115,70,117,110,99]):
               this[a5ce41e255a608030c([111,116,104,101,114,80,114,111,99,101,115,115,70,117,110,99])](obj.param[0],obj.param[1]);
               return;
            default:
               this[obj.func](obj.param);
               return;
         }
      }
   }
   function closePanelFun(ret)
   {
      this._closePanelCallBackFunc(ret);
   }
   function closePanelCallBack(callBackContext, callBackFunc)
   {
      this._closePanelCallBackFunc = AS2_4399_API.Delegate.create(callBackContext,callBackFunc);
   }
   function otherProcessFunc(type, ret)
   {
      switch(type)
      {
         case "serverTimeEvent":
            this._getServerTimeCallBackFunc(ret);
            break;
         case "medalRestartGame":
            this._restartGameCallBackFunc(ret);
         default:
            return;
      }
   }
   function shopProcessFunc(type, ret)
   {
      switch(type)
      {
         case "delItemSuc":
            this._delItemCallBackFunc(ret);
            break;
         case "shopError":
            this._packageErrorCallBackFunc(String(ret));
            break;
         case "getPacakgeInfo":
            this._getPackageCallBackFunc(ret);
            break;
         case "addFreeItemSuc":
            this._addItemsCallBackFunc(ret);
            break;
         case "updateProSuc":
            this._updateItemCallBackFunc(ret);
            break;
         case "getFreePacakgeInfo":
            this._getFreePacCallBackFunc(ret);
            break;
         case "updateExtend":
            this._noticeSetExFlagCallBackFunc(ret);
            break;
         case "addItemSuc":
            this._buyCallBackFunc(ret);
            break;
         case "getPayPacakgeInfo":
            this._getPayPacCallBackFunc(ret);
            break;
         case "getTypeNotice":
            this._noticeTypeCallBackFunc(ret);
            break;
         case "modifyEx":
            this._modifyExCallBackFunc(ret);
            break;
         case "clearItemsByExType":
            this._clearItemsCallBackFunc(ret);
         default:
            return;
      }
   }
   function rankListProcessFunc(type, ret)
   {
      switch(type)
      {
         case "rankListSuccess":
            this._rankListSuccessCallBackFunc(ret);
            break;
         case "rankListError":
            this._rankListErrorCallBackFunc(ret);
         default:
            return;
      }
   }
   function payProcessFunc(type, ret)
   {
      switch(type)
      {
         case "logsuccess":
            if(this.c75362407e1d1b80)
            {
               this.c75362407e1d1b80 = false;
            }
            else
            {
               this._loginCallBackFunc(ret);
            }
            break;
         case "incMoney":
            this._incMoneyInsCallBackFunc(ret);
            break;
         case "decMoney":
            if(this._decMoneyInsCallBackFunc != undefined)
            {
               this._decMoneyInsCallBackFunc(ret);
            }
            if(this._getBalanceCallBackFunc != undefined)
            {
               this._getBalanceCallBackFunc(ret);
            }
            break;
         case "getMoney":
            if(this._getBalanceInsCallBackFunc != undefined)
            {
               this._getBalanceInsCallBackFunc(ret);
            }
            if(this._getBalanceCallBackFunc != undefined)
            {
               this._getBalanceCallBackFunc(ret);
            }
            break;
         case "payMoney":
            this._payMoneyInsCallBackFunc(ret);
            break;
         case "paiedMoney":
            this._getPaiedMoneyCallBackFunc(ret);
            break;
         case "rechargedMoney":
            this._getRechargedMoneyCallBackFunc(ret);
            break;
         case "payError":
            this._payErrorInsCallBackFunc(ret);
            break;
         case "usePayApi":
            this._usePayApiCallBackFunc(ret);
         default:
            return;
      }
   }
   function saveProcessFunc(type, ret)
   {
      if(type == "isLog")
      {
         this._getIsLogCallBackFunc(ret);
      }
      else if(type == "logreturn")
      {
         this._loginCallBackFunc(ret);
      }
      else if(type == "getuserdata")
      {
         this._getDataCallBackFunc(ret);
      }
      else if(type == "saveuserdata")
      {
         this._saveDataCallBackFunc(ret);
      }
      else if(type == "getuserdatalist")
      {
         this._getListCallBackFunc(ret);
      }
      else if(type == "netSaveError")
      {
         this._netSaveErrorCallBackFunc();
      }
      else if(type == "netGetError")
      {
         this._netGetErrorCallBackFunc(ret);
      }
      else if(type == "joinData")
      {
         if(this.joinDataObj.data == undefined)
         {
            this.joinDataObj.data = ret.data;
         }
         else
         {
            this.joinDataObj.data += ret.data;
         }
         if(ret.endFlag == "1")
         {
            this.joinDataObj.index = ret.index;
            this.joinDataObj.datetime = ret.datetime;
            this.joinDataObj.title = ret.title;
            try
            {
               this.joinDataObj.data = AS2_4399_API.JSON.parse(String(this.joinDataObj.data));
            }
            catch(e:Error)
            {
               this.joinDataObj.data = "";
            }
            this._getDataCallBackFunc(this.joinDataObj);
            this.joinDataObj = new Object();
         }
      }
      else if(type == "saveBackIndex")
      {
         this._getSaveUiIdxCallBackFunc(ret);
      }
      else if(type == "multipleError")
      {
         this._multipleErrorCallBackFunc(ret);
      }
      else if(type == "StoreStateEvent")
      {
         this._getStoreStateCallBackFunc(ret);
      }
   }
   function d3516d9c87124bd4(obj)
   {
      if(this[a5ce41e255a608030c([97,48,56,49,102,49,48,55,56,99,51,52,56,53,55,98])] != null)
      {
         this[a5ce41e255a608030c([97,48,56,49,102,49,48,55,56,99,51,52,56,53,55,98])].send(this[a5ce41e255a608030c([97,102,52,48,53,49,102,102,55,50,49,57,97,48,56,56])],a5ce41e255a608030c([114,101,99,101,105,118,101,72,97,110,100,108,101,114]),obj);
      }
   }
   function b3a2761d5a4f7adb(d75659655174056e)
   {
   }
   static function a5ce41e255a608030c(ab608cc046f2a6e6)
   {
      var _loc3_;
      _loc3_ = "";
      var _loc1_ = 0;
      while(_loc1_ < ab608cc046f2a6e6.length)
      {
         _loc3_ += String.fromCharCode(ab608cc046f2a6e6[_loc1_]);
         _loc1_ = _loc1_ + 1;
      }
      return _loc3_;
   }
   function setFocusManager()
   {
      _root.focusManager.enabled = false;
   }
}
