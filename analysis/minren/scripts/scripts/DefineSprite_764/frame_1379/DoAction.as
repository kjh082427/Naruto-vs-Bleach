if(pn == 2)
{
   zn = 1;
   _root.p1bs = "鸣人九尾";
   _parent.中转.ql = ql;
   _parent.中转.hp = hp;
   feixue = function()
   {
      if(_root.zhanting == false)
      {
         if(_root.game.p1.mc.hp > _root.maxhp / 5)
         {
            _root.game.p1.mc.hp -= 10;
         }
      }
   };
}
