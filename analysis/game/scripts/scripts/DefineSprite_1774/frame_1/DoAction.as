qitiao = function()
{
   qi = Math.round(_root.game["p" + nn].mc.ql) + 1;
   bs = Math.floor(_root.game["p" + nn].mc.ql / 100) + 1;
   qt.gotoAndStop(qi);
   bss.gotoAndStop(bs);
};
setInterval(qitiao,300);
tx.namemc.gotoAndStop(_root.p2sf);
