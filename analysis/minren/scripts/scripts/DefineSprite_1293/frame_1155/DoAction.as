if(pn == 1)
{
   zn = 2;
   _root.p2bs = "四尾";
   _parent.中转.ql = ql;
   _parent.中转.hp = hp;
   feixue = function()
   {
      if(_root.zhanting == false)
      {
         if(_root.game.p2.mc.hp > _root.maxhp / 5)
         {
            _root.game.p2.mc.hp -= 10;
         }
      }
   };
}
