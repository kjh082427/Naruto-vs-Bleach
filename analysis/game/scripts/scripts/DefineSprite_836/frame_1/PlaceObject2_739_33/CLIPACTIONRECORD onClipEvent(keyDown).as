onClipEvent(keyDown){
   if(Key.isDown(_root.w))
   {
      _root.keysound1.start();
      if(_parent.cselect == 1)
      {
         _parent.cselect = 6;
      }
      else
      {
         _parent.cselect -= 1;
      }
   }
   if(Key.isDown(_root.s))
   {
      _root.keysound1.start();
      if(_parent.cselect == 6)
      {
         _parent.cselect = 1;
      }
      else
      {
         _parent.cselect += 1;
      }
   }
   if(Key.isDown(_root.j))
   {
      if(_parent.cselect == 1)
      {
         _root.keysound2.start();
         _parent.gotoAndStop("键位设置");
      }
      if(_parent.cselect == 6)
      {
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
         mySO.data.w = _root.w;
         mySO.data.s = _root.s;
         mySO.data.a = _root.a;
         mySO.data.d = _root.d;
         mySO.data.j = _root.j;
         mySO.data.k = _root.k;
         mySO.data.l = _root.l;
         mySO.data.u = _root.u;
         mySO.data.i = _root.i;
         mySO.data.o = _root.o;
         mySO.data.上箭 = _root.上箭;
         mySO.data.下箭 = _root.下箭;
         mySO.data.左箭 = _root.左箭;
         mySO.data.右箭 = _root.右箭;
         mySO.data.N1 = _root.N1;
         mySO.data.N2 = _root.N2;
         mySO.data.N3 = _root.N3;
         mySO.data.N4 = _root.N4;
         mySO.data.N5 = _root.N5;
         mySO.data.N6 = _root.N6;
         mySO.data.maxhp = _root.maxhp;
         mySO.data.AI = _root.AI;
         mySO.data.maxtime = _root.maxtime;
         mySO.data.qualiy = _root._quality;
         _root.keysound2.start();
         _root.gotoAndStop("MENU");
      }
   }
   if(Key.isDown(_root.k))
   {
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
      mySO.data.w = _root.w;
      mySO.data.s = _root.s;
      mySO.data.a = _root.a;
      mySO.data.d = _root.d;
      mySO.data.j = _root.j;
      mySO.data.k = _root.k;
      mySO.data.l = _root.l;
      mySO.data.u = _root.u;
      mySO.data.i = _root.i;
      mySO.data.o = _root.o;
      mySO.data.上箭 = _root.上箭;
      mySO.data.下箭 = _root.下箭;
      mySO.data.左箭 = _root.左箭;
      mySO.data.右箭 = _root.右箭;
      mySO.data.N1 = _root.N1;
      mySO.data.N2 = _root.N2;
      mySO.data.N3 = _root.N3;
      mySO.data.N4 = _root.N4;
      mySO.data.N5 = _root.N5;
      mySO.data.N6 = _root.N6;
      mySO.data.maxhp = _root.maxhp;
      mySO.data.AI = _root.AI;
      mySO.data.maxtime = _root.maxtime;
      mySO.data.qualiy = _root._quality;
      _root.gotoAndStop("MENU");
   }
}
