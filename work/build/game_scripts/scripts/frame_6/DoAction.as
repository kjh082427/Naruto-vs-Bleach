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
addFighterData("日番谷",{name:"히츠가야 토시로",url:"rifagu.swf",fz:"夜一",vs:["一护","一护万解"],says:["강렬한 햇살 아래, 살얼음 위의 발자국은 흔적 없이 사라진다. \n 속는 걸 두려워 마라. 이 세상은 애초에 거짓 위에 세워졌으니.","토시로라고 부르지 마, 히츠가야 대장이다!","아직 멀었어!"]});
addFighterClone("日番谷万解","日番谷",{name:"히츠가야 토시로 만해",WKframe:2,vs:["一护万解","白哉"]});
addFighterData("恋次",{name:"아바라이 렌지",url:"Renji.swf",fz:"石田",vs:["一护","露其雅始解"],says:["닿지 않는 송곳니에 불을 붙인다. 별을 올려다보지 않아도 되는 것처럼, 목이 터져라 외치지 않아도 되는 것처럼.","사실 난 무척 두려워 \n 겉으론 끈질기게 뒤쫓으며 \n 언제든 싸울 수 있는 척하지만 \n 실은 네 그림자조차 밟지 못해 \n 사실, 난 정말 두려워````` "]});
addFighterData("露其雅",{name:"쿠치키 루키아",url:"rukia.swf",fz:"魂",vs:["一护","恋次"],says:["운명은 돌고 도는 걸까? 아니면 앞으로 뻗어 가는 걸까? \n 돌고 도는 거라면, 그 윤회의 고리를 부숴야 할까?  \n 아니면 순순히 받아들여야 할까? ","사람들이 희망을 품을 수 있는 건, 죽음이 보이지 않기 때문이다."]});
addFighterClone("露其雅始解","露其雅",{name:"쿠치키 루키아 시해",WKframe:2,vs:["白哉","一护万解"]});
addFighterData("一护",{name:"쿠로사키 이치고",url:"yihu.swf",fz:"魂",vs:["恋次","露其雅始解"],music:"ichigo.mp3",says:["싸우기만 하는 건 재미없어 그저 살아남기만 하는 것도 의미 없어.","나도 왜인지는 몰라, 아무튼 끝내주는 기분이야! \n 이건… 나의 싸움이다.","보이지 않으니까, 그래서 무서운 거야."]});
addFighterClone("一护万解","一护",{name:"쿠로사키 이치고 만해",WKframe:2,vs:["白哉","日番谷万解"]});
addFighterClone("一护虚化","一护万解",{name:"쿠로사키 이치고 호로화",WKframe:3});
addFighterClone("一护2","一护",{name:"쿠로사키 이치고 0단계",url:"ichigo.swf",fz:"石田"});
addFighterClone("白一护","一护2",{name:"쿠로사키 이치고 내면 호로",WKframe:2,music:"bleachboss.mp3"});
addFighterData("鸣人",{name:"우즈마키 나루토",url:"minren.swf",fz:"我爱罗",vs:["佐助","佐助咒怨"],isNaruto:true,music:"minren.mp3",says:["마을 모두가 인정하는 최고의 닌자가 되면, 호카게라는 이름을 빼앗아 올 수 있어!","난 절대로 포기하지 않아. 그게 나의 닌자의 길이니까!","좋아! 결정했어, 나만의 닌자의 길을 걸을 거야. 절대 후회하지 않을 길을 향해 성큼성큼 계속 걸어갈 거야! "]});
addFighterClone("鸣人九尾","鸣人",{name:"우즈마키 나루토 일미",WKframe:2,vs:["佐助咒怨","鼬"]});
addFighterClone("鸣人九尾实体","鸣人",{name:"우즈마키 나루토 사미",WKframe:3,vs:["佐助咒怨","鼬"]});
addFighterData("樱",{name:"하루노 사쿠라",url:"Sakura.swf",fz:"松本",vs:["手鞠","佐助"],isNaruto:true,says:["난 매번 다른 사람들한테 보호만 받았어, 너무 분해... 그러니까 이번엔... 내가 소중한 사람들을 지켜야 해......","난 매번…… 대단한 닌자가 되길 바랐어……"]});
addFighterData("佐助",{name:"우치하 사스케",url:"Sasuke.swf",fz:"鼬",vs:["鸣人","鸣人九尾"],isNaruto:true,music:"sasuke.mp3",says:["유대가 너무 많으면 자신을 잃을 뿐이다.","고독은 부모에게 꾸중 듣고 슬퍼하는 정도와는 비교도 안 돼.","난 복수자다. 복수를 위해 태어났고, 복수를 위해서라면 모든 걸 버릴 수 있다."]});
addFighterClone("佐助咒怨","佐助",{name:"우치하 사스케 저주인",WKframe:2,vs:["鸣人九尾","鼬"]});
addFighterClone("佐助须佐","佐助",{name:"우치하 사스케 수사노오",url:"sasukexz.swf",vs:["鼬","仙鸣"]});
addFighterData("卡卡西",{name:"하타케 카카시",url:"Kakashi.swf",fz:"我爱罗",vs:["宁次","鼬"],isNaruto:true,says:["닌자는 상식대로 생각해선 안 된다!","걱정 마라, 죽는 한이 있어도 너희는 지킨다. 내 동료는 절대 죽게 두지 않아.","지금의 너로는 날 이길 수 없다. 넌 진정한 강함이 뭔지 전혀 몰라! "]});
addFighterData("剑心",{name:"히무라 켄신",url:"Kenshin.swf",fz:"剑八",vs:["小乌","鼬"],map:"尸魂界通道",music:"bleachboss.mp3",says:["검은 흉기, 검술은 살인 기술. 아무리 아름다운 말로 포장해도 그것이 변치 않는 진실이다"," ...... "]});
addFighterData("白哉",{name:"쿠치키 뱌쿠야",url:"Byakuya.swf",fz:"剑八",vs:["露其雅始解","一护万解"],says:["참으로 둔하군. 쓰러지는 것까지 그 모양이라니.","호오…… 일개 평민이 귀족의 심정을 헤아릴 줄은 몰랐군.","너 같은 자가 내 만해에 죽기엔 천 년은 이르다."]});
addFighterData("茶渡",{name:"사도 야스토라",url:"chad.swf",fz:"织姬",vs:["一护","一护万解"],says:["손에 검을 쥐지 않으면, 널 지킬 수 없어.","검을 계속 쥐고 있으면, 널 안아 줄 수 없어.","......"]});
addFighterData("小李",{name:"록 리",url:"lee.swf",fz:"天天",vs:["佐助","宁次"],isNaruto:true,says:["나는 나뭇잎의 아름다운 푸른 야수, 록 리다 ","지금이야말로 나의 닌자의 길을 관철할 때다!","체술이나 환술을 못 써도 훌륭한 닌자가 될 수 있다는 걸 증명하겠어!"]});
addFighterData("宁次",{name:"휴우가 네지",url:"neji.swf",fz:"雏田",vs:["佐助","宁次"],isNaruto:true,says:["난 단 한 번도—— 상닌이 끝이라고 생각한 적 없다!","사람의 운명은 태어날 때부터 정해져 있다.","운명은, 네 상대가 나로 정해진 순간부터 결정됐다."]});
addFighterData("仙鸣",{name:"우즈마키 나루토 선인 모드",url:"minrenx.swf",fz:"我爱罗",vs:["佐助咒怨","鼬"],map:"火影瀑布",isNaruto:true,says:["마을 모두가 인정하는 최고의 닌자가 되면, 호카게라는 이름을 빼앗아 올 수 있어!","난 절대로 포기하지 않아. 그게 나의 닌자의 길이니까!","좋아! 결정했어, 나만의 닌자의 길을 걸을 거야. 절대 후회하지 않을 길을 향해 성큼성큼 계속 걸어갈 거야! "]});
addFighterClone("黄金鸣人","仙鸣",{name:"우즈마키 나루토 사미",WKframe:2});
addFighterData("小乌",{name:"울키오라",url:"weqal.swf",fz:"织姬",vs:["白一护","一护虚化"],music:"bleachboss.mp3",says:["태양은 이미 우리가 떨어뜨렸다.","내게 보이지 않는 것은 없다","인간이란, 정말 마지막까지 예측할 수 없는 생물이군."]});
addFighterData("手鞠",{name:"테마리",url:"shouju.swf",fzurl:"shouju.swf",fz:"我爱罗",vs:["小李","宁次"],isNaruto:true,says:["바보!","흥!","상대도 안 되네!"]});
addFighterData("石田",{name:"이시다 우류",url:"yulong.swf",fzurl:"yulong.swf",fz:"织姬",vs:["露其雅","一护"],says:["퀸시의 자존심을 걸고, 반드시 널 이기겠다","상대도 안 되는군..."]});
addFighterData("银",{name:"이치마루 긴",url:"yin.swf",fz:"剑八",vs:["一护","白哉"],says:["할 말 없어!","미안해요, 아이젠 대장님.","어쩔 수 없네……"]});
addFighterData("鼬",{name:"우치하 이타치",url:"itachi.swf",fzurl:"you.swf",fz:"我爱罗",vs:["鸣人九尾","佐助咒怨"],map:"宇智波村",isNaruto:true,music:"narutoboss.mp3",says:["뛰어난 것도 나름의 고민이 있는 법이지...","인간이란 그런 거다. 뭔가를 안다고 착각하면 자신이 모르는 것은 부정하고, 자기 지식의 테두리 안에 갇혀 제멋대로 단정할 뿐...","인간은 누구나 자기 지식과 인식에 의지하고, 또 얽매여 살아간다. 그걸 현실이라 부르지. 하지만 지식과 인식은 모호한 것. 현실은 어쩌면 허상일지도 모른다."]});
addFighterData("大蛇丸",{name:"오로치마루",url:"orochimaru.swf",fz:"鼬",vs:["鸣人九尾","佐助咒怨"],isNaruto:true,music:"narutoboss.mp3",says:["조약 따윈 상대를 방심시키기 위한 위장일 뿐. 지금부터 역사는 다시 쓰일 거야","형태가 있는 것은 언젠가 사라지지만, 형태 없는 것은 영원하지!!","육체의 생명은 너무 짧고, 너무 덧없어"]});
addFighterData("蓝染",{name:"아이젠",url:"lanran.swf",fz:"蒂雅",vs:["一护万解","一护虚化"],music:"bleachboss.mp3",says:["이 세상엔 처음부터 진실도 거짓도 없다. 그저 엄연한 사실만이 있을 뿐. 그런데 이 세상 모든 것은 자신에게 유리한 사실만을 진실로 착각하며 살아간다","싸움에 미학을 바라지 마라, 죽음에 미덕을 바라지 마라, 제 목숨만 챙기지 마라. 지킬 가치가 있는 것을 지키고 싶다면, 베어야 할 적은 등 뒤에서라도 베어라","실력에 걸맞지 않은 생명력도 일종의 낭비로군","죽은 자를 비판해선 안 되지","너 같은 수준이 다시 내게 칼끝을 겨누는 건 허락하지 않겠다."]});
addFighterData("魂",{name:"콘",fzurl:"kon.swf"});
addFighterData("夜一",{name:"시호인 요루이치",fzurl:"yeyi.swf"});
addFighterData("织姬",{name:"이노우에 오리히메",fzurl:"zhiji.swf"});
addFighterData("我爱罗",{name:"가아라",url:"gaara.swf",fzurl:"woailuo.swf",fz:"手鞠",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["나는 대체 뭐란 말이냐!","눈에 보이는 놈들은, 전부 죽여 버리겠다!","고작 이 정도냐?"]});
addFighterData("松本",{name:"마츠모토 이노",fzurl:"jinye.swf",isNaruto:true});
addFighterData("剑八",{name:"자라키 켄파치",url:"jianba.swf",fzurl:"jianba.swf",fz:"夜一",vs:["一护万解","一护虚化"],says:["덤벼라, 서로 베어 보자고!","죽음을 두려워하지 않는 건, 죽음을 즐기기 위해서다.","자존심을 버릴 때마다 우린 짐승에 가까워지고, 마음을 죽일 때마다 짐승에게서 한 걸음 멀어진다."]});
addFighterData("天天",{name:"텐텐",fzurl:"tenten.swf",isNaruto:true});
addFighterData("志志雄",{name:"시시오 마코토",fzurl:"shishio.swf"});
addFighterData("自来也",{name:"지라이야",url:"jiraiya.swf",fzurl:"jiraiya.swf",fz:"纲手",vs:["小南","佩恩"],isNaruto:true,says:["동서남북 어디에도 적수가 없는 천하무적의 삼닌, 백발 동자 두꺼비 사용자다.","닌자에게 어떻게 사느냐는 중요하지 않아. 어떻게 죽느냐가 가장 중요하지.","닌자란 참고 견디는 자를 말하는 거다"]});
addFighterData("蒂雅",{name:"티아 할리벨",fzurl:"harribel.swf"});
addFighterData("葛力姆乔",{name:"그림죠 재거잭",fzurl:"grimmjow.swf"});
addFighterData("小南",{name:"코난",url:"konan.swf",fz:"鼬",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["..."]});
addFighterData("佩恩",{name:"페인",url:"pain.swf",fz:"鼬",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["..."]});
addFighterData("带土",{name:"오비토",url:"daitu.swf",fz:"佩恩",vs:["仙鸣","黄金鸣人"],isNaruto:true,says:["동료를 소중히 하지 않는 놈은 쓰레기만도 못해!","현실이 잔혹할수록 마음의 구멍은 커져 간다.","이 세상에 희망 따윈 없다. 희망과 포기는 아무런 차이도 없어. 그저 얼버무리기 위한 핑계일 뿐이다.","난 아무도 아니고, 누가 되고 싶지도 않아...."]});
addFighterData("土影",{name:"츠치카게",isNaruto:true,fzurl:"tuyin.swf"});
addFighterData("四代",{name:"4대 호카게",isNaruto:true,fzurl:"sidai.swf"});
addFighterData("史塔克",{name:"토니 스타크",fzurl:"stake.swf"});
addFighterData("纲手",{name:"츠나데",isNaruto:true,fzurl:"gangshou.swf"});
addFighterData("八千流",{name:"쿠사지시 야치루",fzurl:"baqianliu.swf"});
addFighterData("牛头白一护",{name:"이치고 호로 2단계",fzurl:"yihuxuliu.swf"});
addFighterData("雏田",{name:"휴우가 히나타",isNaruto:true,fzurl:"zhitian.swf"});
addFighterData("碎蜂",{name:"소이퐁",fzurl:"soifong.swf"});
addFighterData("水月",{name:"호오즈키 스이게츠",isNaruto:true,fzurl:"shuiyue.swf"});
addFighterData("涅音梦",{name:"쿠로츠치 네무",fzurl:"nemu.swf"});
addFighterData("佐井",{name:"사이",isNaruto:true,fzurl:"zuojin.swf"});
addFighterData("斑",{name:"우치하 마다라",isNaruto:true,fzurl:"ban.swf"});
addFighterData("一角",{name:"마다라메 잇카쿠",url:"yijiao.swf",fz:"夜一",vs:["一护万解","一护虚化"],says:["우리는 모두 태어난 순간부터 죽음을 향해 걸어간다. ","죽음을 넘어설 수 없는 자는 무언가를 이해해야만 한다.","끝은 언제나 시작되기 전부터 이미 존재한다. "]});
addFighterData("迪达拉",{name:"데이다라",url:"didala.swf",fz:"鼬",vs:["鸣人九尾","仙鸣"],isNaruto:true,says:["예술은 폭발이다! 음.","내 인술은 전부 예술이다! 음.","예술은 아름답고 덧없는 것. 사라지는 그 순간이야말로 아름다운 거다, 음."]});
addFighterData("重吾",{name:"천칭 쥬고",url:"juggo.swf",fz:"鼬",vs:["鸣人九尾","仙鸣"],isNaruto:true,says:["......","하하하하하하","이제 다시는 폭주하지 않아."]});
addFighterData("香磷",{name:"카린",url:"karin.swf",fz:"鼬",vs:["鸣人九尾","鸣人九尾实体"],isNaruto:true,says:["사스케, 나 사스케랑 단둘이......","그때 그 얼굴을 한 번만 더 보고 싶어","사스케, 어디 있어? 기다려 줘......"]});
addFighterData("涅茧利",{name:"쿠로츠치 마유리",url:"mayuri.swf",fz:"鼬",vs:["日番谷万解","一护虚化"],says:["이제 자네에겐 흥미 없네. 저리 비키게.","이런 이런, 내 시간을 이렇게나 낭비하다니.","약물은 하루 8번, 기계 실험은 하루 5번으로 하지. 개조할 때도 되도록 죽이지 않도록 하겠네."]});
addFighterData("奇拉比",{name:"킬러비",url:"qilabi.swf",fz:"鼬",vs:["仙鸣","佐助须佐"],isNaruto:true,says:["이 바보야, 이 자식아!","요! 이 몸이 최강이다! 요!","요! 이 바보야, 이 자식아! 요!......"]});
var mapData = {};
addFighterData("路飞",{name:"몽키 D. 루피",url:"op/luffy.swf",isOnePiece:true,vs:["佐罗","艾斯"],music:"onepiece.mp3",says:["나는 해적왕이 될 남자다!","언젠가 이 녀석들한테 지지 않을 동료들을 모아서, 세계 최고의 보물을 찾아내고 해적왕이 될 거야!!!","해적왕은 내가 된다!"]});
addFighterData("路飞2",{name:"루피 (2년 후)",url:"op/luffy2.swf",isOnePiece:true,vs:["佐罗2","艾斯"],music:"onepiece.mp3",says:["좋아하는 걸 하는 게 제일 중요해!","널 이기지 못하면 아무도 지킬 수 없어.","난 반드시 해적왕이 될 거야!","내 동료한테 손대면 각오해 둬."]});
addFighterData("佐罗",{name:"롤로노아 조로",url:"op/zoro.swf",isOnePiece:true,vs:["香吉","路飞2"],music:"onepiece2.mp3",says:["내겐 야망이 있다. 세계 최고의 검사가 되는 것!!","등에 난 상처는 검사의 수치다!"]});
addFighterData("佐罗2",{name:"조로 (2년 후)",url:"op/zoro2.swf",isOnePiece:true,vs:["香吉","路飞"],music:"onepiece2.mp3",says:["세계 최고의 검사가 될 거다. 악명이 높아지더라도 온 세상에 이름을 떨치겠어.","삼도류는 칼 세 자루를 드는 것과는 다르다.","난세에 태어난 몸, 티끌을 베어 가르리라."]});
addFighterData("香吉",{name:"상디",url:"op/sanji.swf",isOnePiece:true,vs:["佐罗","路飞"],music:"onepiece2.mp3",says:["언젠가… 난 반드시 전설의 바다 '올 블루'를 찾아낼 거다!","바다 위에서 요리사한테 덤비다니 제 무덤을 파는 거야. 잘 기억해 둬… 음식을 함부로 버리지 마.","이건 사랑의 시련이다!","진짜 예의가 뭔지 가르쳐 주지."]});
addFighterData("香吉2",{name:"상디 (2년 후)",url:"op/sanji2.swf",isOnePiece:true,vs:["佐罗2","路飞2"],music:"onepiece2.mp3",says:["언젠가… 난 반드시 전설의 바다 '올 블루'를 찾아낼 거다!","바다 위에서 요리사한테 덤비다니 제 무덤을 파는 거야. 잘 기억해 둬… 음식을 함부로 버리지 마.","이건 사랑의 시련이다!","진짜 예의가 뭔지 가르쳐 주지."]});
addFighterData("娜美",{name:"나미",url:"op/nami.swf",isOnePiece:true,vs:["香吉","路飞"],music:"onepiece2.mp3",says:["이 세상에서 내가 제일 싫어하는 건 해적이야!! 좋아하는 건 돈이랑 귤!","해적의 약탈은 잘못된 거야!! 그러니까 바로잡아 줄 의무가 있어!","내가 배운 항해술로 세계 곳곳을 여행할 거야! 그리고 본 모든 걸 '세계 지도'로 그려 낼 거야!!!","혼자 힘에는 한계가 있어. 뭘 하든 사람에겐 동료가 필요해!"]});
addFighterData("罗宾2",{name:"니코 로빈",url:"op/robin2.swf",isOnePiece:true,vs:["佐罗2","路飞2"],music:"onepiece2.mp3",says:["세상을 볼 땐 진짜 세상을 봐야 해. 자신에게 거짓말을 하면 아무것도 바꿀 수 없어.","말은 아무 소용 없어. 행동해야 의미가 있지.","느끼는 방식과 행동하는 방식을 바꾸면 세상도 바꿀 수 있어."]});
addFighterData("艾斯",{name:"포트거스 D. 에이스",url:"op/ace.swf",isOnePiece:true,vs:["路飞","罗"],music:"onepiece.mp3",says:["사고뭉치 동생이 있으면 형은 늘 걱정이 많지.","흰수염을 해적왕으로 만들 거다!","저주받은 낙인이 날뛰기 시작했군.","잘 들어! 기억해 둬! 루피! 난 죽지 않아!!!"]});
addFighterData("罗",{name:"트라팔가 로",url:"op/law.swf",isOnePiece:true,vs:["佐罗","艾斯"],music:"onepiece3.mp3",says:["약자는 죽는 방법조차 고를 수 없다.","서로 죽이고 싶은 녀석들은 마음대로 하라지. 의미 없는 싸움은 안 해.","입 다물고 따라와. 내 것은 반드시 되찾는다!"]});
addFighterData("甚平",{name:"징베",url:"op/jinbei.swf",isOnePiece:true,music:"onepiece3.mp3",says:["아직 희망을 버릴 순 없다. 난 기적과 기회를 믿는다.","몸은 하나도 안 아프다. 아픈 건 의리를 지키지 못한 이 늙은이의 마음이지.","이 전쟁을 막을 수만 있다면 만 번 죽어도 여한이 없다!"]});
addFighterData("汉库克",{name:"보아 핸콕",url:"op/hancock.swf",isOnePiece:true,vs:["香吉","罗"],music:"onepiece3.mp3",says:["질 리 없다. 첩은 결코 저들에게 지지 않아!","나에게 홀린 마음은 그 몸까지 돌로 굳으리라!","무례한 것, 썩 물러가라!"]});
addFighterData("巴基",{name:"버기",url:"op/buggy.swf",isOnePiece:true,music:"onepiece3.mp3",says:["돌격이다! 이 녀석들아!","발사, 버기 볼!","하하하하하하"]});
addFighterData("克洛克",{name:"크로커다일",url:"op/crocodile.swf",isOnePiece:true,music:"onepiece3.mp3",says:["크하하하!","흥……","모래 폭풍 속으로 사라져라."]});
addFighterData("明哥",{name:"돈키호테 도플라밍고",url:"op/doflamingo.swf",isOnePiece:true,vs:["罗","路飞2"],music:"onepiece3.mp3",says:["정점에 선 자는 선악도 새로 쓸 수 있다! 지금은 이곳만이 중립이야!","정의가 이긴다고? 당연하지. 이긴 자만이 정의니까!","그냥 떠도는 녀석과 큰일을 하기로 각오한 녀석은 얼굴부터 다르지!","약한 놈이 남의 고통에 집착해 봤자 스스로 무너질 뿐이다."]});
addFighterData("米霍克",{name:"쥬라큘 미호크",url:"op/mihawk.swf",isOnePiece:true,WKframe:2,fz:"魂",vs:["佐罗2","香吉2"],music:"onepiece3.mp3",says:["검의 길에 끝은 없다.","그 정도 각오로 나에게 검을 겨누는 건가.","세계 최강의 검사라는 칭호, 그 무게를 보여주지.","약한 자에게 휘두를 검은 없다. 덤벼라."]});
addFighterData("香克斯",{name:"샹크스",url:"op/shanks.swf",isOnePiece:true,fz:"魂",vs:["路飞","米霍克"],music:"onepiece.mp3",says:["이 팔은 새 시대에 걸었다.","친구에게 손대는 녀석은 용서 못 해.","싸움을 끝내러 왔다.","자, 술이나 한잔하자고."]});
addMapData("现世",{name:"현세",frame:"现世",music:"city.mp3"});
addMapData("流魂街",{name:"유혼가",frame:"流魂街",music:"village.mp3"});
addMapData("双极",{name:"쌍극",frame:"双极",music:"wind.mp3"});
addMapData("静涎亭",{name:"정령정",frame:"静涎亭",music:"village.mp3"});
addMapData("尸魂界通道",{name:"소울 소사이어티 통로",frame:"尸魂界通道",music:"sahndong.mp3"});
addMapData("木叶村",{name:"나뭇잎 마을",frame:"木叶村",music:"village.mp3"});
addMapData("温泉",{name:"온천",frame:"温泉",music:"water.mp3"});
addMapData("火影瀑布",{name:"종말의 계곡",frame:"火影瀑布",music:"pubu.mp3"});
addMapData("楼顶",{name:"옥상",frame:"楼顶",music:"wind.mp3"});
addMapData("宇智波村",{name:"우치하 일족",frame:"宇智波村",music:"wind.mp3"});
var bleachMusic = "bleach.mp3";
var narutoMusic = "naruto.mp3";

var selectableIds = ["一护","一护万解","一护2","露其雅","露其雅始解","恋次","日番谷","日番谷万解","白哉","茶渡","石田","小乌","银","剑八","一角","涅茧利","蓝染","剑心","鸣人","鸣人九尾","仙鸣","佐助","佐助咒怨","佐助须佐","樱","卡卡西","小李","宁次","手鞠","我爱罗","鼬","大蛇丸","自来也","佩恩","小南","带土","迪达拉","重吾","香磷","奇拉比","路飞","路飞2","佐罗","佐罗2","香吉","香吉2","娜美","罗宾2","艾斯","罗","甚平","汉库克","巴基","克洛克","明哥","米霍克","香克斯"];
