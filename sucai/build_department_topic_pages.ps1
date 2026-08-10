$ErrorActionPreference = "Stop"

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$templatePath = Join-Path $baseDir "department-showcase-page.html"
$template = [IO.File]::ReadAllText($templatePath, [Text.Encoding]::UTF8)

$source = @{
  title = "毕节职业技术学院数字文旅专题"
  aria = "毕节职业技术学院数字文旅专题展示页"
  topic = "数字文旅专题"
  tagline = "山水人文 · 智慧导览 · 酒店运营 · 文旅服务"
  card1 = "文旅资源概况"
  aria1 = "毕节山水文旅资源"
  p1 = "依托百里杜鹃、织金洞、乌江源百里画廊与乌蒙山水资源，构建地方文化、生态旅游与智慧服务融合场景。"
  card2 = "专业群建设"
  aria2 = "数字文旅专业群建设"
  p2 = "围绕旅游管理、酒店运营、数字媒体与景区服务，培养懂文化、会运营、能策划、善服务的复合型文旅人才。"
  card3 = "实训基地"
  aria3 = "智慧景区与酒店服务实训基地"
  p3 = "建设智慧景区导览、酒店前厅客房、研学策划、数字内容制作等实训空间，强化真实服务流程训练。"
  partner1 = "景区协同育人"
  partner2 = "酒店企业共建"
  partner3 = "研学基地实践"
  partner4 = "数字内容服务"
  partnerP = "与景区、酒店、旅行服务机构和数字文旅企业共建实践项目，开展课程共建、岗位实训与服务创新。"
  result1 = "景区服务实训"
  result2 = "文旅内容策划"
  result3 = "智慧导览应用"
  result4 = "研学服务案例"
  resultP = "学生参与导览服务、活动策划、酒店运营与数字内容制作，服务地方景区提升、文旅品牌传播与研学项目落地。"
  story1P = "《智慧景区服务与运营》课程资源建设与应用"
  story2P = "AR导览路线与游客服务小程序学生创新项目"
  story3P = "在旅游服务、数字媒体与创新创业赛事中获得奖项"
  story4Title = "研学服务"
  story4Aria = "研学服务"
  story4P = "师生团队参与地方研学路线设计与文旅志愿服务"
  videoAria = "毕节数字文旅宣传片"
  videoTitle = "毕节数字文旅专题宣传片"
  videoP = "展示学院围绕智慧景区、酒店服务、数字导览与地方文化传播的教学成果和实践探索。"
}

$topics = @(
  @{
    slug = "modern-agriculture"
    file = "department-modern-agriculture.html"
    bg = "页面/背景1.png"
    title = "毕节职业技术学院现代农业专题"
    aria = "毕节职业技术学院现代农业专题展示页"
    topic = "现代农业专题"
    tagline = "山地特色 · 智慧农业 · 产教融合 · 乡村振兴"
    card1 = "山地农业概况"; aria1 = "山地农业梯田"; p1 = "立足乌蒙山地资源禀赋，聚焦马铃薯、天麻、茶叶、肉牛、食用菌等特色产业，服务乡村振兴战略。"
    card2 = "专业群建设"; aria2 = "现代农业专业群建设"; p2 = "构建现代农业技术、农产品加工、数字化生产服务等方向，培养山地特色高效农业技术技能人才。"
    card3 = "实训基地"; aria3 = "智慧农业实训基地"; p3 = "建设智慧温控、无人机植保、食用菌实训、农产品检测等实训基地，强化实践教学与真实生产对接。"
    partner1 = "农业企业合作"; partner2 = "合作社共建"; partner3 = "生产基地共建"; partner4 = "订单培养定制"; partnerP = "与农业龙头企业、合作社共建生产基地，开展订单培养、技术服务与协同创新，促进人才培养与产业需求精准融合。"
    result1 = "学业实践实训"; result2 = "农产品品牌打造"; result3 = "数字测控应用"; result4 = "社会服务案例"; resultP = "学生深度参与生产实践，助力农产品品牌建设、数字田间管理与电商营销，服务地方产业与乡村发展。"
    story1P = "《山地特色作物栽培》课程资源建设与应用"; story2P = "智慧温室环境调控系统学生创新项目"; story3P = "在农业技能与创新创业赛事中获得奖项"; story4Title = "乡村服务"; story4Aria = "乡村服务"; story4P = "师生团队深入村镇开展技术指导与产业帮扶"
    videoAria = "现代山地特色高效农业宣传片"; videoTitle = "现代山地特色高效农业宣传片"; videoP = "展示学院在山地农业、实践教学与产教融合方面的办学成果与实践探索。"
    ink = "#40523b"; green = "#42643f"; gold = "#bc9440"; rose = "#8aa46c"; body = "#f4eddf"; viewport = "#ede2cf"; h1 = "#3e5f3d"; soft = "#61705c"; primary = "#365f35"; secondary = "#bc9641"; gradient = "#5f7b4f, #c2a052"; play = "#436238"
  },
  @{
    slug = "digital-tourism"
    file = "department-digital-tourism.html"
    bg = "页面/digital-tourism-bg.png"
    title = "毕节职业技术学院数字文旅专题"
    aria = "毕节职业技术学院数字文旅专题展示页"
    topic = "数字文旅专题"
    tagline = "山水人文 · 智慧导览 · 酒店运营 · 文旅服务"
    card1 = "文旅资源概况"; aria1 = "毕节山水文旅资源"; p1 = "依托百里杜鹃、织金洞、乌江源百里画廊与乌蒙山水资源，构建地方文化、生态旅游与智慧服务融合场景。"
    card2 = "专业群建设"; aria2 = "数字文旅专业群建设"; p2 = "围绕旅游管理、酒店运营、数字媒体与景区服务，培养懂文化、会运营、能策划、善服务的复合型文旅人才。"
    card3 = "实训基地"; aria3 = "智慧景区与酒店服务实训基地"; p3 = "建设智慧景区导览、酒店前厅客房、研学策划、数字内容制作等实训空间，强化真实服务流程训练。"
    partner1 = "景区协同育人"; partner2 = "酒店企业共建"; partner3 = "研学基地实践"; partner4 = "数字内容服务"; partnerP = "与景区、酒店、旅行服务机构和数字文旅企业共建实践项目，开展课程共建、岗位实训与服务创新。"
    result1 = "景区服务实训"; result2 = "文旅内容策划"; result3 = "智慧导览应用"; result4 = "研学服务案例"; resultP = "学生参与导览服务、活动策划、酒店运营与数字内容制作，服务地方景区提升、文旅品牌传播与研学项目落地。"
    story1P = "《智慧景区服务与运营》课程资源建设与应用"; story2P = "AR导览路线与游客服务小程序学生创新项目"; story3P = "在旅游服务、数字媒体与创新创业赛事中获得奖项"; story4Title = "研学服务"; story4Aria = "研学服务"; story4P = "师生团队参与地方研学路线设计与文旅志愿服务"
    videoAria = "毕节数字文旅宣传片"; videoTitle = "毕节数字文旅专题宣传片"; videoP = "展示学院围绕智慧景区、酒店服务、数字导览与地方文化传播的教学成果和实践探索。"
    ink = "#314b4c"; green = "#36666a"; gold = "#bb9051"; rose = "#c97d8f"; body = "#eef0e8"; viewport = "#e9eee9"; h1 = "#335e60"; soft = "#5c7370"; primary = "#356c70"; secondary = "#bf9150"; gradient = "#4f8b8a, #c97d8f 54%, #c9a15c"; play = "#376f73"
  },
  @{
    slug = "smart-healthcare"
    file = "department-smart-healthcare.html"
    bg = "页面/smart-healthcare-bg.png"
    title = "毕节职业技术学院智慧康养专题"
    aria = "毕节职业技术学院智慧康养专题展示页"
    topic = "智慧康养专题"
    tagline = "护理康养 · 急救教育 · 健康管理 · 智慧服务"
    card1 = "护理康养概况"; aria1 = "护理康养与健康服务"; p1 = "面向护理照护、老年康养、健康管理与急救教育需求，结合毕节生态康养资源，打造温暖专业的健康服务育人场景。"
    card2 = "专业群建设"; aria2 = "智慧康养专业群建设"; p2 = "围绕护理、康复照护、健康管理与服务运营，培养兼具人文关怀、规范操作和数字应用能力的技能人才。"
    card3 = "护理实训基地"; aria3 = "护理康养实训基地"; p3 = "建设护理床旁照护、急救训练、康复照护、生命体征监测与健康数据管理等实训模块，强化真实岗位流程训练。"
    partner1 = "医院协同育人"; partner2 = "康养机构共建"; partner3 = "社区健康服务"; partner4 = "急救培训项目"; partnerP = "与医疗机构、康养中心和社区服务单位共建实践基地，开展岗位实训、健康宣教与社会服务。"
    result1 = "护理技能实训"; result2 = "健康管理项目"; result3 = "急救培训成果"; result4 = "社区服务案例"; resultP = "学生参与护理照护、健康档案管理、急救科普和社区服务，形成面向地方民生需求的实践成果。"
    story1P = "《智慧康养服务实务》课程资源建设与应用"; story2P = "健康数据随访与康养服务流程学生项目"; story3P = "在护理技能与健康服务竞赛中获得奖项"; story4Title = "社区服务"; story4Aria = "社区健康服务"; story4P = "师生团队开展健康宣教、急救培训与康养志愿服务"
    videoAria = "智慧康养专题宣传片"; videoTitle = "智慧康养专题宣传片"; videoP = "展示学院围绕护理实训、康养服务、健康管理与急救教育的教学成果和实践探索。"
    ink = "#375457"; green = "#2f8584"; gold = "#c79566"; rose = "#d8759a"; body = "#f4f0ed"; viewport = "#e9f2ef"; h1 = "#2e7476"; soft = "#637c7b"; primary = "#2f8584"; secondary = "#d8759a"; gradient = "#42a7a3, #d8759a 56%, #c79566"; play = "#2f8584"
  },
  @{
    slug = "finance-commerce"
    file = "department-finance-commerce.html"
    bg = "页面/finance-commerce-bg.png"
    title = "毕节职业技术学院财经商贸专题"
    aria = "毕节职业技术学院财经商贸专题展示页"
    topic = "财经商贸专题"
    tagline = "数字商贸 · 电商物流 · 财务管理 · 产教服务"
    card1 = "商贸服务概况"; aria1 = "财经商贸服务场景"; p1 = "面向区域商贸流通、乡村电商、农特产品上行和数字物流需求，构建财经商贸综合服务能力。"
    card2 = "专业群建设"; aria2 = "财经商贸专业群建设"; p2 = "围绕大数据与会计、电子商务、现代物流、市场营销等方向，培养懂经营、会核算、善运营的技能人才。"
    card3 = "实训基地"; aria3 = "数字商贸实训基地"; p3 = "建设直播电商、财务共享、物流沙盘、商务数据分析等实训空间，强化经营流程与真实业务对接。"
    partner1 = "企业财务实践"; partner2 = "电商平台共建"; partner3 = "物流企业协同"; partner4 = "乡村电商服务"; partnerP = "与商贸企业、电商平台、物流机构和地方产业项目共建实践任务，开展订单培养与真实项目训练。"
    result1 = "财务实训成果"; result2 = "直播电商项目"; result3 = "物流方案设计"; result4 = "社会服务案例"; resultP = "学生参与账务处理、电商运营、物流方案设计和产品推广，服务地方商贸升级与品牌传播。"
    story1P = "《数字商贸运营》课程资源建设与应用"; story2P = "农特产品电商运营与数据分析学生项目"; story3P = "在财经商贸与创新创业赛事中获得奖项"; story4Title = "电商服务"; story4Aria = "电商服务"; story4P = "师生团队参与地方产品推广、直播运营与商贸服务"
    videoAria = "财经商贸专题宣传片"; videoTitle = "财经商贸专题宣传片"; videoP = "展示学院围绕财务管理、电子商务、物流运营与产教服务的教学成果和实践探索。"
    ink = "#4b463a"; green = "#53634f"; gold = "#bd8c43"; rose = "#c47b52"; body = "#f1eee6"; viewport = "#ece8dc"; h1 = "#4b5c48"; soft = "#706a5b"; primary = "#59684f"; secondary = "#bd8c43"; gradient = "#667159, #c47b52 54%, #c7a45f"; play = "#5f704d"
  },
  @{
    slug = "digital-tech"
    file = "department-digital-tech.html"
    bg = "页面/digital-tech-bg.png"
    title = "毕节职业技术学院数智技术专题"
    aria = "毕节职业技术学院数智技术专题展示页"
    topic = "数智技术专题"
    tagline = "人工智能 · 网络安全 · 数据应用 · 跨专业赋能"
    card1 = "数智技术概况"; aria1 = "数智技术应用场景"; p1 = "面向人工智能、网络安全、数据应用和数字化转型需求，打造服务多专业融合的数智技术能力平台。"
    card2 = "专业群建设"; aria2 = "数智技术专业群建设"; p2 = "围绕软件开发、网络安全、数据治理、智能应用等方向，培养能开发、会运维、懂安全的复合型技术人才。"
    card3 = "实训基地"; aria3 = "数智技术实训基地"; p3 = "建设AI应用、网络安全攻防、云平台运维、数据分析等实训环境，强化项目制与任务式教学。"
    partner1 = "科技企业合作"; partner2 = "平台课程共建"; partner3 = "网安实训项目"; partner4 = "数据服务实践"; partnerP = "与科技企业、平台服务商和行业应用单位共建项目，开展课程共创、认证训练与真实案例实践。"
    result1 = "AI应用项目"; result2 = "网络安全实训"; result3 = "数据分析成果"; result4 = "数字赋能案例"; resultP = "学生参与智能应用开发、网络安全演练、数据分析和跨专业数字化项目，提升解决真实问题的能力。"
    story1P = "《人工智能应用基础》课程资源建设与应用"; story2P = "校园数据助手与智能问答学生创新项目"; story3P = "在网络安全与软件开发赛事中获得奖项"; story4Title = "数字赋能"; story4Aria = "数字赋能"; story4P = "师生团队为专业教学与管理场景提供数字化服务"
    videoAria = "数智技术专题宣传片"; videoTitle = "数智技术专题宣传片"; videoP = "展示学院围绕人工智能、网络安全、数据应用和跨专业赋能的教学成果与实践探索。"
    ink = "#34464c"; green = "#2f6975"; gold = "#c49a56"; rose = "#48a6a4"; body = "#eef1f1"; viewport = "#e8eeee"; h1 = "#2f626f"; soft = "#607377"; primary = "#2f707b"; secondary = "#c49a56"; gradient = "#42a7a7, #4d8ca4 54%, #c49a56"; play = "#2f707b"
  },
  @{
    slug = "smart-energy"
    file = "department-smart-energy.html"
    bg = "页面/smart-energy-bg.png"
    title = "毕节职业技术学院智慧能源专题"
    aria = "毕节职业技术学院智慧能源专题展示页"
    topic = "智慧能源专题"
    tagline = "绿色能源 · 智能开采 · 化工安全 · 低碳转型"
    card1 = "能源产业概况"; aria1 = "智慧能源产业场景"; p1 = "面向绿色能源、智能开采、化工安全和低碳转型需求，构建服务地方能源产业升级的教学场景。"
    card2 = "专业群建设"; aria2 = "智慧能源专业群建设"; p2 = "围绕能源装备、化工安全、智能监测、绿色低碳等方向，培养懂工艺、会监测、守安全的技术人才。"
    card3 = "实训基地"; aria3 = "智慧能源实训基地"; p3 = "建设能源监测、化工安全、设备运维、传感器应用等实训模块，强化安全规范与产业流程对接。"
    partner1 = "能源企业合作"; partner2 = "安全实训共建"; partner3 = "设备运维实践"; partner4 = "低碳项目服务"; partnerP = "与能源企业、化工园区和设备服务单位共建实践项目，开展岗位训练、安全培训和技术服务。"
    result1 = "安全技能实训"; result2 = "能源监测应用"; result3 = "设备运维项目"; result4 = "低碳服务案例"; resultP = "学生参与安全演练、能源数据监测、设备巡检和低碳服务项目，提升产业现场综合实践能力。"
    story1P = "《智慧能源安全与运维》课程资源建设与应用"; story2P = "能源监测与设备预警学生创新项目"; story3P = "在能源装备与安全技能赛事中获得奖项"; story4Title = "低碳服务"; story4Aria = "低碳服务"; story4P = "师生团队参与节能诊断、安全宣教与绿色发展服务"
    videoAria = "智慧能源专题宣传片"; videoTitle = "智慧能源专题宣传片"; videoP = "展示学院围绕绿色能源、智能开采、化工安全和低碳转型的教学成果与实践探索。"
    ink = "#3d4d43"; green = "#3f7858"; gold = "#c6a24a"; rose = "#83a857"; body = "#eef0e7"; viewport = "#e8eee4"; h1 = "#3d6b50"; soft = "#647568"; primary = "#3d7858"; secondary = "#c3a047"; gradient = "#4e9b68, #9ab65d 54%, #d0a94e"; play = "#3f7858"
  },
  @{
    slug = "intelligent-manufacturing"
    file = "department-intelligent-manufacturing.html"
    bg = "页面/intelligent-manufacturing-bg.png"
    title = "毕节职业技术学院智能制造专题"
    aria = "毕节职业技术学院智能制造专题展示页"
    topic = "智能制造专题"
    tagline = "智能装备 · 新能源汽车 · 无人机应用 · 数字工厂"
    card1 = "制造产业概况"; aria1 = "智能制造产业场景"; p1 = "面向智能装备、新能源汽车、无人机应用和数字工厂需求，构建现代制造业技术技能培养场景。"
    card2 = "专业群建设"; aria2 = "智能制造专业群建设"; p2 = "围绕数控加工、工业机器人、汽车技术、无人机应用等方向，培养懂工艺、会操作、能维护的制造人才。"
    card3 = "实训基地"; aria3 = "智能制造实训基地"; p3 = "建设工业机器人、数控加工、汽车实训、无人机应用与质量检测等实训空间，强化产线任务训练。"
    partner1 = "制造企业合作"; partner2 = "产线项目共建"; partner3 = "设备运维实践"; partner4 = "订单培养定制"; partnerP = "与装备制造、汽车服务和工业技术企业共建实践项目，开展产线实训、项目教学和岗位能力培养。"
    result1 = "设备操作实训"; result2 = "工艺优化项目"; result3 = "技能竞赛成果"; result4 = "企业服务案例"; resultP = "学生参与设备调试、工艺优化、检测维护和企业项目服务，提升面向智能制造现场的综合能力。"
    story1P = "《智能制造产线运行》课程资源建设与应用"; story2P = "无人机巡检与工业检测学生创新项目"; story3P = "在智能制造与装备技能赛事中获得奖项"; story4Title = "企业服务"; story4Aria = "企业服务"; story4P = "师生团队参与设备维护、工艺改进与技术服务"
    videoAria = "智能制造专题宣传片"; videoTitle = "智能制造专题宣传片"; videoP = "展示学院围绕智能装备、新能源汽车、无人机应用与数字工厂的教学成果和实践探索。"
    ink = "#43484a"; green = "#56656b"; gold = "#c18445"; rose = "#d1743f"; body = "#eeeeea"; viewport = "#e8e9e6"; h1 = "#46565c"; soft = "#667075"; primary = "#596b72"; secondary = "#c18445"; gradient = "#6f7f83, #d1743f 58%, #c19658"; play = "#5b6d73"
  },
  @{
    slug = "campus-culture"
    file = "department-campus-culture.html"
    bg = "页面/campus-culture-bg.png"
    title = "毕节职业技术学院同心校园文化专题"
    aria = "毕节职业技术学院同心校园文化专题展示页"
    topic = "同心校园文化"
    tagline = "同心育人 · 校园文化 · 学生成长 · 服务地方"
    card1 = "文化育人概况"; aria1 = "同心校园文化场景"; p1 = "围绕同心育人、民族团结、校园文化和学生成长，构建有温度、有归属感的校园文化展示场景。"
    card2 = "育人体系建设"; aria2 = "校园文化育人体系"; p2 = "融合思政教育、社团活动、志愿服务、心理健康和成长支持，形成多元协同的文化育人体系。"
    card3 = "活动阵地"; aria3 = "校园文化活动阵地"; p3 = "建设文化展示、社团活动、阅读空间、志愿服务和学生发展等阵地，记录师生成长与校园活力。"
    partner1 = "同心育人活动"; partner2 = "社团品牌共建"; partner3 = "志愿服务实践"; partner4 = "文化传承项目"; partnerP = "联动校内外资源开展主题教育、社团品牌、志愿服务和文化传承项目，促进学生全面成长。"
    result1 = "校园活动成果"; result2 = "学生成长案例"; result3 = "志愿服务项目"; result4 = "文化品牌建设"; resultP = "学生参与社团实践、志愿服务、文化活动和成长项目，形成有辨识度的校园文化品牌与育人成果。"
    story1P = "《同心校园文化育人》主题资源建设与应用"; story2P = "校园文化地图与成长档案学生项目"; story3P = "在校园文化、志愿服务与创新活动中获得奖项"; story4Title = "志愿服务"; story4Aria = "志愿服务"; story4P = "师生团队参与社区服务、文化传播与成长陪伴活动"
    videoAria = "同心校园文化专题宣传片"; videoTitle = "同心校园文化专题宣传片"; videoP = "展示学院围绕同心育人、校园文化、学生成长与服务地方的活动成果和实践探索。"
    ink = "#4f493d"; green = "#4f6b61"; gold = "#ba8c45"; rose = "#b8574f"; body = "#f2eee6"; viewport = "#eee8dd"; h1 = "#4f6a61"; soft = "#746a5d"; primary = "#4f6b61"; secondary = "#b8574f"; gradient = "#5f8477, #b8574f 54%, #c59b55"; play = "#4f6b61"
  }
)

function Replace-Text($html, $from, $to) {
  return $html.Replace($from, $to)
}

function Build-Override($topic) {
  $bg = $topic.bg
  return @"

    /* Topic override: $($topic.topic) */
    :root {
      --ink: $($topic.ink);
      --green: $($topic.green);
      --gold: $($topic.gold);
      --rose: $($topic.rose);
    }

    body { background: $($topic.body); }
    .viewport { background: $($topic.viewport); }
    .page { background-image: url("$bg"); }
    h1 { color: $($topic.h1); }
    .tagline { color: $($topic.soft); }
    .seal { border-color: $($topic.primary); }
    .seal::before,
    .panel-title .icon,
    .partner-icons span::before,
    .result-item::before {
      background: linear-gradient(135deg, $($topic.gradient));
    }
    .round-link.green { background: $($topic.primary); }
    .round-link.gold { background: $($topic.secondary); }
    .dots span:first-child,
    .arrow.next { background: $($topic.primary); }
    .play::before { border-left-color: $($topic.play); }
    .video-copy strong { color: $($topic.h1); }
    .photo {
      background-image: linear-gradient(180deg, rgba(255,255,255,0), rgba(31,76,80,0.14)), url("$bg");
    }
    .video-box {
      background-image:
        linear-gradient(90deg, rgba(15, 43, 47, 0.24), rgba(15, 43, 47, 0.04)),
        linear-gradient(0deg, rgba(8, 22, 26, 0.68), transparent 36%),
        url("$bg");
    }
    .film-chip { background-image: url("$bg"); }
"@
}

$generated = @()

foreach ($topic in $topics) {
  $html = $template
  foreach ($key in $source.Keys) {
    $html = Replace-Text $html $source[$key] $topic[$key]
  }
  $html = $html.Replace('  </style>', "$(Build-Override $topic)`n  </style>")
  $outputPath = Join-Path $baseDir $topic.file
  [IO.File]::WriteAllText($outputPath, $html, [Text.UTF8Encoding]::new($false))
  $generated += [PSCustomObject]@{ Topic = $topic.topic; File = $topic.file }
}

$links = $generated | ForEach-Object {
  "        <a href=""$($_.File)"">$($_.Topic)</a>"
}

$index = @"
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>毕节职业技术学院专题二级页面</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #eef0e8;
      color: #314b4c;
      font-family: "Microsoft YaHei UI", "PingFang SC", "Noto Sans SC", Arial, sans-serif;
    }
    main {
      width: min(980px, calc(100vw - 48px));
      padding: 40px;
      border-radius: 24px;
      background: rgba(255, 253, 248, 0.9);
      box-shadow: 0 20px 52px rgba(55, 73, 69, 0.14);
    }
    h1 { margin: 0 0 24px; font-size: 34px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
    a {
      display: block;
      padding: 18px 20px;
      border: 1px solid rgba(178, 157, 118, 0.32);
      border-radius: 14px;
      color: inherit;
      text-decoration: none;
      font-size: 20px;
      font-weight: 800;
      background: rgba(255,255,255,0.7);
    }
    a:hover { border-color: #bb9051; }
  </style>
</head>
<body>
  <main>
    <h1>专题二级页面</h1>
    <div class="grid">
$($links -join "`n")
    </div>
  </main>
</body>
</html>
"@

[IO.File]::WriteAllText((Join-Path $baseDir "department-topic-index.html"), $index, [Text.UTF8Encoding]::new($false))
$generated | Format-Table -AutoSize
