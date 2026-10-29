function addFighterData(id, obj)
{
   fighterData[id] = obj;
}
function addFighterClone(newid, cloneid, modobj)
{
   var _loc1_ = {};
   var _loc2_ = getFighterData(cloneid);
   for(var _loc4_ in _loc2_)
   {
      _loc1_[_loc4_] = _loc2_[_loc4_];
   }
   for(_loc4_ in modobj)
   {
      _loc1_[_loc4_] = modobj[_loc4_];
   }
   addFighterData(newid,_loc1_);
}
function getFighterData(id)
{
   return fighterData[id];
}
function addMapData(id, obj)
{
   mapData[id] = obj;
}
function getMapData(id)
{
   return mapData[id];
}
var fighterData = {};
addFighterData("日番谷",{name:"日番谷·东狮郎",url:"rifagu.swf",fz:"夜一",vs:["一护","一护万解"],says:["在强烈的阳光下，印在薄冰之上的足迹消失无踪。 \n 不必害怕被欺骗，这世界原本就建立在假象之上。","不要叫我冬狮郎，是日番谷队长!","还差得远呢！"]});
addFighterClone("日番谷万解","日番谷",{name:"日番谷·东狮郎 卍解",WKframe:2,vs:["一护万解","白哉"]});
addFighterData("恋次",{name:"阿散井·恋次",url:"Renji.swf",fz:"石田",vs:["一护","露其雅始解"],says:["在触不到的燎牙上点火，就象不必仰望星星就能解决，就象不必喊破喉咙就可以一样。","其实我非常害怕 \n 虽然表面好像紧追不舍 \n 随时可以应战了 \n 实际上，我却连你的影子都不敢踩 \n 其实，我真的很害怕````` "]});
addFighterData("露其雅",{name:"朽木·露琪亚",url:"rukia.swf",fz:"魂",vs:["一护","恋次"],says:["命运是轮回的吗?还是伸向前方的? \n 假如,是轮回的话,那就应该把那轮回之环击碎吗?  \n 还是应该逆来顺受呢? ","人们之所以能怀抱希望，是因为他们看不见死亡。"]});
addFighterClone("露其雅始解","露其雅",{name:"朽木·露琪亚 始解",WKframe:2,vs:["白哉","一护万解"]});
addFighterData("一护",{name:"黑崎·一护",url:"yihu.swf",fz:"魂",vs:["恋次","露其雅始解"],music:"ichigo.mp3",says:["光是战斗根本没有意思 只是活下去也没有意义。","我也不知道为什么，总之很爽就是了! \n 这是…我的战斗。","正因为我们看不见，那才可怕。"]});
addFighterClone("一护万解","一护",{name:"黑崎·一护 卍解",WKframe:2,vs:["白哉","日番谷万解"]});
addFighterClone("一护虚化","一护万解",{name:"黑崎·一护 虚化",WKframe:3});
addFighterClone("一护2","一护",{name:"黑崎·一护 零段",url:"ichigo.swf",fz:"石田"});
addFighterClone("白一护","一护2",{name:"黑崎·一护 内虚",WKframe:2,music:"bleachboss.mp3"});
addFighterData("鸣人",{name:"漩涡·鸣人",url:"minren.swf",fz:"我爱罗",vs:["佐助","佐助咒怨"],isNaruto:true,music:"minren.mp3",says:["只要你变成全村人都认可的最棒忍者，你就可以把火影这个名字抢过来！","我是绝对不会放弃的，因为这就是我的忍道！","好!我决定了,我要走一条属于我自己的忍道,朝着绝对不让自己后悔的道路一直大步的走下去! "]});
addFighterClone("鸣人九尾","鸣人",{name:"漩涡·鸣人 一尾",WKframe:2,vs:["佐助咒怨","鼬"]});
addFighterClone("鸣人九尾实体","鸣人",{name:"漩涡·鸣人 四尾",WKframe:3,vs:["佐助咒怨","鼬"]});
addFighterData("樱",{name:"春野·樱",url:"Sakura.swf",fz:"松本",vs:["手鞠","佐助"],isNaruto:true,says:["我每次都受到其他人的保护，好不甘心哦...既然如此，这次...必须有我来保护我所珍惜的人们了......","我每次……都希望自己能够成为一个厉害的忍者……"]});
addFighterData("佐助",{name:"宇智波·佐助",url:"Sasuke.swf",fz:"鼬",vs:["鸣人","鸣人九尾"],isNaruto:true,music:"sasuke.mp3",says:["羁绊太多，只会迷失自我。","孤独，不是被父母责备后难过的那种程度比得上的。","我是个复仇者，我是为复仇而生的，为了复仇我可以放弃一切。"]});
addFighterClone("佐助咒怨","佐助",{name:"宇智波·佐助 咒怨",WKframe:2,vs:["鸣人九尾","鼬"]});
addFighterClone("佐助须佐","佐助",{name:"宇智波·佐助 须佐能乎",url:"sasukexz.swf",vs:["鼬","仙鸣"]});
addFighterData("卡卡西",{name:"旗木·卡卡西",url:"Kakashi.swf",fz:"我爱罗",vs:["宁次","鼬"],isNaruto:true,says:["忍者是不能按常理来思考的！","放心吧，就算死我也会保护你们的，我绝对不让我的同伴被杀。","以现在的你是赢不了我的，你根本不明白什么是真正的强大！ "]});
addFighterData("剑心",{name:"绯村·剑心",url:"Kenshin.swf",fz:"剑八",vs:["小乌","鼬"],map:"尸魂界通道",music:"bleachboss.mp3",says:["剑是凶器，剑技是杀人的伎俩，无论用多么美丽的语言去掩饰，那始终是事实"," ...... "]});
addFighterData("白哉",{name:"朽木·白哉",url:"Byakuya.swf",fz:"剑八",vs:["露其雅始解","一护万解"],says:["真是迟钝啊。连倒下去都是这样。","喔……真没想到一介平民也能体会贵族的感受啊。","像你这种人，死在我的万解之下，还早了一千年。"]});
addFighterData("茶渡",{name:"茶渡·泰虎",url:"chad.swf",fz:"织姬",vs:["一护","一护万解"],says:["如果手上没有剑，我就不能保护你。","如果我一直握着剑，我就无法抱紧你。","......"]});
addFighterData("小李",{name:"李·洛克",url:"lee.swf",fz:"天天",vs:["佐助","宁次"],isNaruto:true,says:["我是木叶美丽的青色之兽、李洛克 ","现在就是我贯彻我的忍道的时候了！","我要证明就算不会用体术或幻术也能成为一个了不起的忍者！"]});
addFighterData("宁次",{name:"日向·宁次",url:"neji.swf",fz:"雏田",vs:["佐助","宁次"],isNaruto:true,says:["我从来都不认为——上忍就是终点！","人的命运，是从一出生就被注定了。","命运，从对手是我的那一刻开始便被决定了。"]});
addFighterData("仙鸣",{name:"漩涡·鸣人 仙人",url:"minrenx.swf",fz:"我爱罗",vs:["佐助咒怨","鼬"],map:"火影瀑布",isNaruto:true,says:["只要你变成全村人都认可的最棒忍者，你就可以把火影这个名字抢过来！","我是绝对不会放弃的，因为这就是我的忍道！","好!我决定了,我要走一条属于我自己的忍道,朝着绝对不让自己后悔的道路一直大步的走下去! "]});
addFighterClone("黄金鸣人","仙鸣",{name:"漩涡·鸣人 四尾",WKframe:2});
addFighterData("小乌",{name:"乌尔奇奥拉",url:"weqal.swf",fz:"织姬",vs:["白一护","一护虚化"],music:"bleachboss.mp3",says:["太阳已经被我们击落了。","没有什么是我看不到的","人类，真是到最后，也出人意料的生物。"]});
addFighterData("手鞠",{name:"手鞠",url:"shouju.swf",fzurl:"shouju.swf",fz:"我爱罗",vs:["小李","宁次"],isNaruto:true,says:["笨蛋!","哼！","不堪一击！"]});
addFighterData("石田",{name:"石田·雨龙",url:"yulong.swf",fzurl:"yulong.swf",fz:"织姬",vs:["露其雅","一护"],says:["我赌上灭却师的骄傲，一定要赢你","不堪一击..."]});
addFighterData("银",{name:"市丸·银",url:"yin.swf",fz:"剑八",vs:["一护","白哉"],says:["我无话可说！","对不起，蓝染队长。","真没办法……"]});
addFighterData("鼬",{name:"宇智波·鼬",url:"itachi.swf",fzurl:"you.swf",fz:"我爱罗",vs:["鸣人九尾","佐助咒怨"],map:"宇智波村",isNaruto:true,music:"narutoboss.mp3",says:["优秀也是有烦恼的...","人类就是这样，自以为自己知道了什么，就否定了自己不知道的东西，只会局限在自己的知识范围内自以为是...","只要是人，都是依靠自己的知识与认知并且也被之束缚生活着的，那就叫做现实。但是，知识与认知是暧昧不清的东西，现实也许只是镜花水月。"]});
addFighterData("大蛇丸",{name:"大蛇丸",url:"orochimaru.swf",fz:"鼬",vs:["鸣人九尾","佐助咒怨"],isNaruto:true,music:"narutoboss.mp3",says:["条约只是让对手麻痹的伪装，从现在开始历史将被改写","有形的东西迟早会毁灭，无形的东西才会永恒！！","肉体的生命太短暂,太无常"]});
addFighterData("蓝染",{name:"蓝染",url:"lanran.swf",fz:"蒂雅",vs:["一护万解","一护虚化"],music:"bleachboss.mp3",says:["这个世界在最初并没有真实,也没有谎言,只有俨然存在的事实,可是,存在于这个世界的所有事物,只会将对自己有利的事实误认为真实而活","别要求战斗应该具备美学,别要求死亡必须遵从美德,别只顾成全一己性命,如果想守护那值得守护的事物,就从背后斩杀那应该斩杀的敌人","与实力并不相称的生命力也是一种浪费啊","不能批判死者","像你这样的水准,我不准你再次对我刀刃相向."]});
addFighterData("魂",{name:"魂",fzurl:"kon.swf"});
addFighterData("夜一",{name:"四枫院·夜一",fzurl:"yeyi.swf"});
addFighterData("织姬",{name:"井上·织姬",fzurl:"zhiji.swf"});
addFighterData("我爱罗",{name:"我爱罗",url:"gaara.swf",fzurl:"woailuo.swf",fz:"手鞠",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["我到底是什么啊!","我要把我看到的所有人,通通杀光!","就只有这样而已吗?"]});
addFighterData("松本",{name:"松本·井野",fzurl:"jinye.swf",isNaruto:true});
addFighterData("剑八",{name:"更木·剑八",url:"jianba.swf",fzurl:"jianba.swf",fz:"夜一",vs:["一护万解","一护虚化"],says:["来吧、厮杀吧!","不畏惧死，为的是玩乐死亡。","每舍弃自尊一次，我们就越像是野兽。每扼杀一颗心，我们就远离野兽一步。"]});
addFighterData("天天",{name:"天天",fzurl:"tenten.swf",isNaruto:true});
addFighterData("志志雄",{name:"志志雄·真实",fzurl:"shishio.swf"});
addFighterData("自来也",{name:"自来也",url:"jiraiya.swf",fzurl:"jiraiya.swf",fz:"纲手",vs:["小南","佩恩"],isNaruto:true,says:["不分东南西北，整个天下都是无人能敌的三忍白发童子蛤蟆使者。","对于忍者而言怎样活着无所谓，怎样死去才是最重要的。","忍者指的是能忍耐的人"]});
addFighterData("蒂雅",{name:"蒂雅·赫丽贝尔",fzurl:"harribel.swf"});
addFighterData("葛力姆乔",{name:"葛力姆乔·贾卡杰克",fzurl:"grimmjow.swf"});
addFighterData("小南",{name:"小南",url:"konan.swf",fz:"鼬",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["..."]});
addFighterData("佩恩",{name:"佩恩",url:"pain.swf",fz:"鼬",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["..."]});
addFighterData("带土",{name:"带土",url:"daitu.swf",fz:"佩恩",vs:["仙鸣","黄金鸣人"],isNaruto:true,says:["不重视同伴的人，连废物都不如!","现实越残酷，内心的空洞就越大。","这个世界已无所谓的希望，希望和放弃没有任何的区别，只是一种敷衍的托词罢了。","我谁也不是，也不想变成谁。。。。"]});
addFighterData("土影",{name:"土影",isNaruto:true,fzurl:"tuyin.swf"});
addFighterData("四代",{name:"四代火影",isNaruto:true,fzurl:"sidai.swf"});
addFighterData("史塔克",{name:"托尼·斯塔克",fzurl:"stake.swf"});
addFighterData("纲手",{name:"纲手",isNaruto:true,fzurl:"gangshou.swf"});
addFighterData("八千流",{name:"草鹿·八千流",fzurl:"baqianliu.swf"});
addFighterData("牛头白一护",{name:"一护·虚·二段",fzurl:"yihuxuliu.swf"});
addFighterData("雏田",{name:"日向·雏田",isNaruto:true,fzurl:"zhitian.swf"});
addFighterData("碎蜂",{name:"碎蜂",fzurl:"soifong.swf"});
addFighterData("水月",{name:"鬼灯·水月",isNaruto:true,fzurl:"shuiyue.swf"});
addFighterData("涅音梦",{name:"涅音梦",fzurl:"nemu.swf"});
addFighterData("佐井",{name:"佐井",isNaruto:true,fzurl:"zuojin.swf"});
addFighterData("斑",{name:"宇智波·斑",isNaruto:true,fzurl:"ban.swf"});
addFighterData("一角",{name:"斑目·一角",url:"yijiao.swf",fz:"夜一",vs:["一护万解","一护虚化"],says:["我们每个人，打从出生的那一刻起就要迈向死亡。 ","无法超越死亡的人，那就必须去理解某些事。","结束总是在开始之前就已经存在了了。 "]});
addFighterData("迪达拉",{name:"迪达拉",url:"didala.swf",fz:"鼬",vs:["鸣人九尾","仙鸣"],isNaruto:true,says:["艺术就是爆炸!嗯。","我的忍术全都是艺术！嗯。","艺术是美丽而短暂的，消失那一瞬间 才称为美丽，嗯。"]});
addFighterData("重吾",{name:"天秤·重吾",url:"juggo.swf",fz:"鼬",vs:["鸣人九尾","仙鸣"],isNaruto:true,says:["......","哈哈哈哈哈哈","我不会再失控了。"]});
addFighterData("香磷",{name:"香磷",url:"karin.swf",fz:"鼬",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["佐助，人家想和佐助两个人......","真想再看一次他那时的面庞","佐助，你在哪里？等等我......"]});
addFighterData("涅茧利",{name:"涅茧利",url:"mayuri.swf",fz:"鼬",vs:["日番谷万解","一护虚化"],says:["我已经对你没兴趣了，闪一变去。","哎呀哎呀，浪费了我这么多时间。","药物每天8次，机器实验就每天5次吧，而改造我也会尽量避免把你搞死。"]});
addFighterData("奇拉比",{name:"奇拉比",url:"qilabi.swf",fz:"鼬",vs:["仙鸣","佐助须佐"],isNaruto:true,says:["你这笨蛋，你这混蛋！","哟！本大爷是最强的！哟！","哟！你这笨蛋，你这混蛋！哟！......"]});
var mapData = {};
addMapData("现世",{name:"现世",frame:"现世",music:"city.mp3"});
addMapData("流魂街",{name:"流魂街",frame:"流魂街",music:"village.mp3"});
addMapData("双极",{name:"双极",frame:"双极",music:"wind.mp3"});
addMapData("静涎亭",{name:"静涎亭",frame:"静涎亭",music:"village.mp3"});
addMapData("尸魂界通道",{name:"尸魂界通道",frame:"尸魂界通道",music:"sahndong.mp3"});
addMapData("木叶村",{name:"木叶村",frame:"木叶村",music:"village.mp3"});
addMapData("温泉",{name:"温泉",frame:"温泉",music:"water.mp3"});
addMapData("火影瀑布",{name:"终结之谷",frame:"火影瀑布",music:"pubu.mp3"});
addMapData("楼顶",{name:"楼顶",frame:"楼顶",music:"wind.mp3"});
addMapData("宇智波村",{name:"宇智波一族",frame:"宇智波村",music:"wind.mp3"});
var bleachMusic = "bleach.mp3";
var narutoMusic = "naruto.mp3";
