onClipEvent(keyUp){
   if(_parent.cselect == 1)
   {
      _root.txtst = 0;
      _root.txt = "键位设置";
   }
   if(_parent.cselect == 2)
   {
      _root.txtst = 0;
      if(_parent.cmlv.cl == 1)
      {
         _root.txt = "电脑等级 : 非常简单";
      }
      if(_parent.cmlv.cl == 2)
      {
         _root.txt = "电脑等级 : 简单";
      }
      if(_parent.cmlv.cl == 3)
      {
         _root.txt = "电脑等级 : 中等";
      }
      if(_parent.cmlv.cl == 4)
      {
         _root.txt = "电脑等级 : 困难";
      }
      if(_parent.cmlv.cl == 5)
      {
         _root.txt = "电脑等级 : 非常困难";
      }
   }
   if(_parent.cselect == 3)
   {
      _root.txtst = 0;
      if(_parent.qulity.cl == 1)
      {
         _root.txt = "画质设置 : 高质量";
      }
      if(_parent.qulity.cl == 2)
      {
         _root.txt = "画质设置 : 中等质量";
      }
      if(_parent.qulity.cl == 3)
      {
         _root.txt = "画质设置 : 低质量";
      }
   }
   if(_parent.cselect == 4)
   {
      _root.txtst = 0;
      if(_parent.gtime.cl == 1)
      {
         _root.txt = "时间设置 : 30秒";
      }
      if(_parent.gtime.cl == 2)
      {
         _root.txt = "时间设置 : 60秒";
      }
      if(_parent.gtime.cl == 3)
      {
         _root.txt = "时间设置 : 90秒";
      }
      if(_parent.gtime.cl == 4)
      {
         _root.txt = "时间设置 : 无限时";
      }
   }
   if(_parent.cselect == 5)
   {
      _root.txtst = 0;
      _root.txt = "生命设置 : " + _parent.plife.cl * 100 + "%";
   }
   if(_parent.cselect == 6)
   {
      _root.txtst = 0;
      _root.txt = "回主菜单";
   }
}
