onClipEvent(enterFrame){
   if(an == 0)
   {
      if(_parent.anj == 0)
      {
         if(Key.isDown(_root.w))
         {
            _root.keysound1.start();
            if(select == 1)
            {
               select = 9;
            }
            else
            {
               select -= 1;
            }
            an = 1;
         }
         if(Key.isDown(_root.s))
         {
            _root.keysound1.start();
            if(select == 8)
            {
               select = 11;
            }
            else
            {
               select += 1;
            }
            an = 1;
         }
         if(Key.isDown(_root.j))
         {
            _root.keysound2.start();
            _parent["btm" + select].play();
            _parent.anj = 1;
         }
      }
   }
   if(_parent["btm" + select]._y < -5)
   {
      i = 1;
      while(i < 15)
      {
         _parent["btm" + i]._y += spd;
         i++;
      }
   }
   if(_parent["btm" + select]._y > 5)
   {
      i = 1;
      while(i < 15)
      {
         _parent["btm" + i]._y -= spd;
         i++;
      }
   }
   if(_parent["btm" + select]._y > -6 and _parent["btm" + select]._y < 6)
   {
      if(select == 9)
      {
         _parent.btm1._y = -403.5;
         _parent.btm2._y = -347.6;
         _parent.btm3._y = -291.7;
         _parent.btm4._y = -235.8;
         _parent.btm5._y = -173.9;
         _parent.btm6._y = -112;
         _parent.btm7._y = -56.1;
         _parent.btm8._y = -0.2;
         _parent.btm9._y = -460.3;
         _parent.btm10._y = -516.2;
         _parent.btm11._y = 56.1;
         _parent.btm12._y = 112;
         select = 8;
      }
      if(select == 11)
      {
         _parent.btm1._y = 0.1;
         _parent.btm2._y = 56;
         _parent.btm3._y = 111.9;
         _parent.btm4._y = 167.8;
         _parent.btm5._y = 229.7;
         _parent.btm6._y = 291.6;
         _parent.btm7._y = 347.5;
         _parent.btm8._y = 403.4;
         _parent.btm9._y = -58.8;
         _parent.btm10._y = -114.7;
         _parent.btm11._y = 459.7;
         _parent.btm12._y = 515.6;
         select = 1;
      }
      if(an == 1)
      {
         _root.txtst = 0;
      }
      an = 0;
      if(select == 1 or select == 11)
      {
         _root.txt = "일반 1인 모드";
      }
      if(select == 2 or select == 12)
      {
         _root.txt = "CPU와 대전";
      }
      if(select == 3)
      {
         _root.txt = "2인 대전";
      }
      if(select == 4)
      {
         _root.txt = "격투 연습";
      }
      if(select == 5)
      {
         _root.txt = "게임 설정 · 키 설정";
      }
      if(select == 6)
      {
         _root.txt = "게임 관련 정보 설명";
      }
      if(select == 7 or select == 10)
      {
         _root.txt = "더 많은 재밌는 게임";
      }
      if(select == 8 or select == 9)
      {
         _root.txt = "게임 종료";
      }
   }
}
