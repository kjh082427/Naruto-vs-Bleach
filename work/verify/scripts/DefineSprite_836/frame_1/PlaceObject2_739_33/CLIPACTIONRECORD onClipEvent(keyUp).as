onClipEvent(keyUp){
   if(_parent.cselect == 1)
   {
      _root.txtst = 0;
      _root.txt = "키 설정";
   }
   if(_parent.cselect == 2)
   {
      _root.txtst = 0;
      if(_parent.cmlv.cl == 1)
      {
         _root.txt = "CPU 레벨 : 매우 쉬움";
      }
      if(_parent.cmlv.cl == 2)
      {
         _root.txt = "CPU 레벨 : 쉬움";
      }
      if(_parent.cmlv.cl == 3)
      {
         _root.txt = "CPU 레벨 : 보통";
      }
      if(_parent.cmlv.cl == 4)
      {
         _root.txt = "CPU 레벨 : 어려움";
      }
      if(_parent.cmlv.cl == 5)
      {
         _root.txt = "CPU 레벨 : 매우 어려움";
      }
   }
   if(_parent.cselect == 3)
   {
      _root.txtst = 0;
      if(_parent.qulity.cl == 1)
      {
         _root.txt = "화질 설정 : 높음";
      }
      if(_parent.qulity.cl == 2)
      {
         _root.txt = "화질 설정 : 보통";
      }
      if(_parent.qulity.cl == 3)
      {
         _root.txt = "화질 설정 : 낮음";
      }
   }
   if(_parent.cselect == 4)
   {
      _root.txtst = 0;
      if(_parent.gtime.cl == 1)
      {
         _root.txt = "시간 설정 : 30초";
      }
      if(_parent.gtime.cl == 2)
      {
         _root.txt = "시간 설정 : 60초";
      }
      if(_parent.gtime.cl == 3)
      {
         _root.txt = "시간 설정 : 90초";
      }
      if(_parent.gtime.cl == 4)
      {
         _root.txt = "시간 설정 : 무제한";
      }
   }
   if(_parent.cselect == 5)
   {
      _root.txtst = 0;
      _root.txt = "체력 설정 : " + _parent.plife.cl * 100 + "%";
   }
   if(_parent.cselect == 6)
   {
      _root.txtst = 0;
      _root.txt = "메인 메뉴로";
   }
}
