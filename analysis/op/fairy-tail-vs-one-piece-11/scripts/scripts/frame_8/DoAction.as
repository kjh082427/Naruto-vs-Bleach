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
function getRandMap()
{
   for(var _loc1_ in mapData)
   {
      if(Math.random() < 0.3)
      {
         return _loc1_;
      }
   }
   return _loc1_;
}
var fighterData = {};
var mapData = {};
addFighterData("路飞",{name:"Luffy",url:"luffy.swf",vs:["佐罗","艾斯"],map:"雪地",music:"onepiece.mp3",says:["我是要成为海贼王的男人！ ","总有一天，我会聚集一群不输给这些人的伙伴，并找到世界第一的财宝，我要当上海贼王！！！！ ","海贼王，我当定了！"]});
addFighterData("路飞2",{name:"Luffy-2Y",url:"luffy2.swf",vs:["佐罗2","艾斯"],map:"雪地",music:"onepiece.mp3",says:["做喜欢的事才是最重要的! ","不战胜你的话就保护不了任何人。 ","我一定会成为海贼王！","敢对我的伙伴出手，就要做好心理准备。"]});
addFighterData("佐罗",{name:"Zoro",url:"zoro.swf",vs:["香吉","路飞2"],map:"海底",says:["我有个野心，就是要成为世界第一的剑士！！ ","背后中剑，是剑士的耻辱！"]});
addFighterData("佐罗2",{name:"Zoro-2Y",url:"zoro2.swf",vs:["香吉","路飞"],map:"海底",says:["我要成为世界第一的剑客，就算是恶名昭彰我也要扬名全世界。  ","三刀流和拿三把刀，是不一样的。","吾乃生于乱世中，自当斩破尘埃。"]});
addFighterData("巴基",{name:"Buggy",url:"buggy.swf",says:["冲啊！伙计们！","发射，巴基弹!","哈哈哈哈哈哈"]});
addFighterData("克洛克",{name:"Crocodile",url:"crocodile.swf",says:["呵哈哈！","哼......","消失在沙暴中吧"]});
addFighterData("香吉",{name:"Sanji",url:"sanji.swf",vs:["佐罗","路飞"],map:"树林",says:["总有一天……我一定会找到“ＡＬＬ　ＢＬＵＥ”传说之海的！","敢在海上和厨师作对，简直是自寻死路，你好好记着…别随便糟蹋食物…… ","这是爱的试练！","让我来教你真正的礼仪之道"]});
addFighterData("香吉2",{name:"Sanji",url:"sanji2.swf",vs:["佐罗2","路飞2"],map:"树林",says:["总有一天……我一定会找到“ＡＬＬ　ＢＬＵＥ”传说之海的！","敢在海上和厨师作对，简直是自寻死路，你好好记着…别随便糟蹋食物…… ","这是爱的试练！","让我来教你真正的礼仪之道"]});
addFighterData("罗宾2",{name:"Nico Robin",url:"robin2.swf",vs:["佐罗2","路飞2"],map:"树林",says:["看世界要看到真实的世界，千万不要向自己撒谎。你对自己都撒谎，那么你不可能改变。为什么很多人要夸大事实因为他们害怕失败。","任何谈论都是没有用的，只有去做才有用。","改变感觉的方式，改变做事情的方式就可以改变世界。"]});
addFighterData("甚平",{name:"Jinbei",url:"jinbei.swf",map:"海边",says:["还不能抛弃希望，我相信奇迹和机会。","我的身体根本不痛，痛的是不能行侠仗义的老夫的心。","若能阻止这场战争，老夫万死不辞！"]});
addFighterData("罗",{name:"Law",url:"law.swf",vs:["佐罗","艾斯"],map:"雪地",says:["弱者，连死的方式都无权选择。","喜欢互相残杀的家伙就让他们互相残杀去就好，我不打无意义的仗。","闭上嘴乖乖地跟着我，属于我的东西，我一定会夺回来！"]});
addFighterData("汉库克",{name:"Hancock",url:"hancock.swf",vs:["香吉","罗"],map:"海边",says:["不会输的，妾身绝不会输给他们的！","受我诱惑之心，必将硬化汝等身躯！","无礼之人，给我退下！"]});
addFighterData("娜美",{name:"Nami",url:"nami.swf",vs:["香吉","路飞"],map:"海边",says:["在这个世界上，我最讨厌的，就是海贼！！我喜欢钱和橘子！","我个人认为海贼的掠夺行为事错误的！！所以，我有义务要纠正他们！！  ","我要用我所学到的航海技术，到世界各地去旅行！再把我所看到的一切，画成一张“世界地图”！！！","一个人的力量是有限度的，不论想做什么事，一个人的力量是不够的，人是需要同伴的！"]});
addFighterData("艾斯",{name:"Ace",url:"ace.swf",vs:["路飞","罗"],map:"沙漠",says:["有个爱闯祸的弟弟，哥哥总是要特别担心。 ","我要让白胡子称王！","诅咒的烙印已经开始发作了","听好了！给我记住！路飞！我是不会死的！！！"]});
addFighterData("明哥",{name:"Doflamingo",url:"doflamingo.swf",is_fairy:false,vs:["罗","路飞2"],map:"树林",says:["站在顶点的人可以重新书写善恶!现在只有这个地方才是中立啊!正义会胜?那是当然的吧，只有胜者，才是正义啊!","正义会胜？ 那是当然的吧，只有胜者，才是正义啊！","纯粹的流浪的人士和抱定决心干大事的人其相貌可不大一样！","弱小的家伙，还要执着于他人的痛苦，只会自取灭亡。"]});
addFighterData("纳兹",{name:"Natsu",url:"natsu.swf",is_fairy:true,vs:["格雷","艾露莎"],map:"妖精屋内",says:["我们要是为了保护家人，国家也好，世界也好，通通都可以视为敌人!","你准备好成为妖精的尾巴的敌人了吗?","不要被打败了就罗里罗嗦！我们可是来自妖精的尾巴，是不知阻挠为何物的协会，不继续走下去的话就生存不了！"]});
addFighterData("格雷",{name:"Gray",url:"gray.swf",is_fairy:true,vs:["纳兹","艾露莎"],map:"妖精屋内",says:["这就是我所选择的道路，是我必须去做的事。","只要有同伴，公会就会存在。","抱歉了，不管是女人还是小孩，凡是伤害我伙伴的人，我都不会原谅的!"]});
addFighterData("露西",{name:"Lucy",url:"lucy.swf",is_fairy:true,vs:["格雷","纳兹"],map:"妖精城市",says:["我最喜欢妖精尾巴了！","妖精尾巴绝对不会饶过你们的！","我啊…觉得如果不是跟大家在一起的话，我一定无法生存下去。","星灵不是盾牌！一起作战才是我的风格！"]});
addFighterData("艾露莎",{name:"Ersa",url:"ersa.swf",is_fairy:true,vs:["纳兹","米拉杰"],map:"妖精屋外",music:"ersa.mp3",says:["如果你不想输给任何人，你先要知道自己的软弱，并且，保有温柔。","不是为了伙伴而死，而是为了伙伴活下去。这才是通往幸福的道路。","就算到了尽头拿着木棒我也会战斗到底！"]});
addFighterData("葛吉尔",{name:"Gajeel",url:"gajeel.swf",is_fairy:true,vs:["温蒂","纳兹"],map:"冥府之门",says:["哼！本大爷是最强的！","开什么玩笑？","怎么能输给你呢？我绝对不能输啊！我是妖精的尾巴的魔导士啊！"]});
addFighterData("温蒂",{name:"Wendy",url:"wendy.swf",is_fairy:true,vs:["露西","葛吉尔"],map:"妖精城市",says:["我想我们可以帮助他们。","我想保护妖精的尾巴，请助我一臂之力。","就算魔力已经全部用尽，我到最后一刻为止都不会放弃的，这就是妖精尾巴。"]});
addFighterData("米拉杰",{name:"Mirajane",url:"mirajane.swf",is_fairy:true,vs:["纳兹","艾露莎"],map:"妖精屋外",music:"ersa.mp3",says:["这样的战斗…太空虚了。","我不认为依赖一个人有什么不对，在你的身边有许许多多的人，人与人之间总是紧密相连。","我…现在的我，虽然没有战斗的力量，不过…我一定要保护同伴！"]});
addFighterData("拉克萨斯",{name:"Laxus",url:"lasasi.swf",is_fairy:true,vs:["纳兹","艾露莎"],map:"妖精屋外",says:["我是想让这个公会更加强大。","爷爷！你的时代已经过去了！","我是妖精的尾巴，最强的魔导师！"]});
addFighterData("朱比亚",{name:"Juvia",url:"juvia.swf",is_fairy:true,vs:["纳兹","艾露莎"],map:"妖精屋外",says:["如果让我伤害别人的话，让我伤害同伴的话，就让朱比亚作铺路石好了！","朱比亚非常喜欢妖精尾巴。大家都为同伴着想，非常快乐，十分温暖。。","既然有爱就必须要活下去。！","格雷大人!~~~~~ 等等我!~~~~"]});
addFighterData("马克洛夫",{name:"Makarov",url:"makarov.swf",is_fairy:true,vs:["纳兹","艾露莎"],map:"妖精屋外",says:["妖精是不是有尾巴？妖精是否存在其实都 没人知道。正因为如此，永远的谜题就是 永恒的冒险。","无论悲伤的事，还是快乐的事，虽然不能说全部如此，但可以某种程度的共有，这就是工会。一个人的幸福，就是大家的幸福；一个人的愤怒，就是大家的愤怒；并且，一个人的眼泪，也是大家的眼泪。","总有一天，你们会明白，到底是因为人死会悲伤还是因为悲伤会杀死人。"]});
var opStages = ["温蒂","露西","格雷","葛吉尔","纳兹"];
var opBoss = ["艾露莎","米拉杰"];
var fairyStages = ["娜美","香吉","佐罗","汉库克","路飞"];
var fairyBoss = ["路飞2","明哥"];
addMapData("树林",{name:"树林",frame:"树林",music:"sunny.mp3",weather:["晴","雷雨"]});
addMapData("沙漠",{name:"沙漠",frame:"沙漠",music:"desert.mp3",weather:["晴"]});
addMapData("海边",{name:"海边",frame:"海边",music:"sea.mp3",weather:["大雨","雷雨"]});
addMapData("雪地",{name:"冻岛",frame:"雪地",music:"desert.mp3",weather:["晴","雪"]});
addMapData("海底",{name:"鱼人岛",frame:"海底",music:"sea.mp3",weather:["水泡"]});
addMapData("妖精屋外",{name:"公会(外面)",frame:"妖精屋外",music:"sunny.mp3",weather:["晴","大雨"]});
addMapData("妖精屋内",{name:"公会(里面)",frame:"妖精屋内",music:"fairytail.mp3",weather:["晴"]});
addMapData("妖精城市",{name:"城市",frame:"妖精城市",music:"fairytail.mp3",weather:["晴","大雨","雷雨"]});
addMapData("铁路",{name:"山中铁路",frame:"铁路",music:"wind.mp3",weather:["晴"]});
addMapData("冥府之门",{name:"冥府之门公会内",frame:"冥府之门",music:"fairytail.mp3",weather:["晴"]});
var fairyMusic = ["fairytail.mp3","fairytail2.mp3","fairytail3.mp3"];
var opMusic = ["onepiece.mp3","onepiece2.mp3","onepiece3.mp3"];
var rainMusic = "rain.mp3";
