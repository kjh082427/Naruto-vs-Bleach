function clean()
{
   txt.text = txt2.text = "";
}
stop();
wenzi = function()
{
   if(_root.txtst <= mblength(_root.txt))
   {
      _root.txtst = _root.txtst + 1;
      txt.text = mbsubstring(_root.txt,1,_root.txtst);
   }
   if(_root.txtst2 <= mblength(_root.txt2))
   {
      _root.txtst2 = _root.txtst2 + 1;
      txt2.text = mbsubstring(_root.txt2,1,_root.txtst2);
   }
};
_root.wzset = setInterval(wenzi,30);
