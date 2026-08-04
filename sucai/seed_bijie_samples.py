from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "expo.db"
DOCX_PATH = ROOT / "sucai" / "毕节职业技术学院成果样例.docx"
UPLOAD_DIR = ROOT / "uploads" / "bijie-samples"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_media() -> dict[str, str]:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    urls: dict[str, str] = {}
    with ZipFile(DOCX_PATH) as docx:
        for name in docx.namelist():
            if not name.startswith("word/media/") or name.endswith("/"):
                continue
            target = UPLOAD_DIR / Path(name).name
            target.write_bytes(docx.read(name))
            urls[Path(name).stem] = f"/uploads/bijie-samples/{target.name}"
    return urls


def page_body_social(media: dict[str, str]) -> str:
    return f"""
<div class="lead-card"><span>SOCIAL SERVICE</span><strong>服务地方产业与技能人才培养</strong><p>学校围绕毕节新发展理念示范区建设，聚焦现代能源、生态食品、先进装备制造、轻纺及健康医药等产业，持续开展职业技能培训、等级认定和乡村振兴服务。</p></div>
<div class="stat-grid"><div class="stat"><strong>45000+</strong><span>培训人次</span><p>联合政校企完成多类型技术技能培训。</p></div><div class="stat"><strong>15000+</strong><span>认定人次</span><p>面向学生和社会人员开展职业技能等级认定。</p></div><div class="stat"><strong>八大产业</strong><span>服务方向</span><p>对接地方工业产业和特色农业发展需求。</p></div></div>
<h2>重点服务方向</h2><ul><li>高技能人才、基层服务、煤矿安全技术、退役军人就业创业培训。</li><li>乡村振兴技能人才培养和非物质文化遗产传承人群研修研习。</li><li>职业技能等级认定与专项职业能力认定平台建设。</li></ul>
<div class="photo-strip"><figure><img src="{media['image1']}" alt="培训现场"><figcaption>毕节市财政财务基础业务培训班</figcaption></figure><figure><img src="{media['image16']}" alt="稻米示范推广培训"><figcaption>优质稻米示范推广培训进入田间地头</figcaption></figure></div>
<blockquote>以学校技术资源和师资优势服务地方产业发展，助力毕节市人力资源开发和乡村全面振兴。</blockquote>
""".strip()


def page_body_international(media: dict[str, str]) -> str:
    return f"""
<div class="lead-card"><span>GLOBAL COOPERATION</span><strong>从“引进来”到“走出去”的国际合作</strong><p>学校主动服务“一带一路”倡议和中国-东盟、中非教育合作，在海外交流、标准输出、多边合作、技能竞赛、人文往来等方面形成阶段性成果。</p></div>
<div class="timeline"><div><span>2024</span><p>组织师生赴泰国格乐大学开展短期研学，拓宽学生国际视野，增进中泰人文交流。</p></div><div><span>2025</span><p>牵头制定菲律宾《农业经理人》国家职业技能标准，并参与中国-东盟数字资源共建共享合作。</p></div><div><span>近三年</span><p>累计接待国（境）外来访团组 4 个，举办国际文化交流活动 4 场，签订校际合作备忘录 2 份。</p></div></div>
<h2>成果看点</h2><ul><li>获批埃塞俄比亚国家职业标准开发项目认证。</li><li>课程资源被俄罗斯喀山联邦大学、埃塞俄比亚 Dire Dawa University 采用。</li><li>师生在金砖国家技能发展与技术创新大赛等国际赛事中获得多项奖项。</li></ul>
<div class="photo-strip"><figure><img src="{media['image23']}" alt="泰国研学合影"><figcaption>师生赴泰国格乐大学开展短期研学</figcaption></figure><figure><img src="{media['image31']}" alt="国际人文交流活动"><figcaption>“桥见”贵州毕节职院人文交流活动</figcaption></figure></div>
<hr><p>这一页用于测试时间线、图文组合、列表与分隔线在大屏详情页中的可读性。</p>
""".strip()


def page_body_graduate(media: dict[str, str]) -> str:
    return f"""
<div class="profile-card"><img src="{media['image38']}" alt="张娅婷事迹照片"><div><span>优秀毕业生</span><h3>张娅婷</h3><p>贵州省 2024 届优秀毕业生，学前教育专业。她在校园学习、学生工作、志愿服务和西部计划实践中持续成长。</p></div></div>
<div class="badge-list"><span>中共党员</span><span>教育科学系</span><span>学前教育</span><span>国家奖学金</span><span>省级优秀毕业生</span></div>
<h2>一路追光，筑梦前行</h2><p>在校期间，她担任系学生会团总支副书记、学生会主席、班级团支部书记与班长，荣获全国乡村振兴“笃行计划优秀实践个人”、励志奖学金、省三好学生等荣誉。</p>
<h3>敢担当</h3><p>2021 年至 2023 年，她承担学生组织工作，并于 2023 年赴马来西亚英迪国际大学短期访学，按期高质量完成学业。</p>
<h3>能吃苦</h3><p>连续两年参加“三下乡”社会实践，组织关爱留守儿童、服务空巢老人和民族文化传承活动，在实践中锤炼专业能力和社会责任。</p>
<h3>有理想</h3><p>2024 年 8 月，她投身贵州省毕节市七星关区碧阳街道办事处西部计划志愿服务，参与档案整理、热线回应和志愿服务等工作。</p>
<div class="template-note"><strong>教师评语</strong><p>希望你用行动去诠释教育的真谛，展现青春的力量。</p></div>
""".strip()


def page_body_teacher(media: dict[str, str]) -> str:
    return f"""
<div class="profile-card"><img src="{media['image39']}" alt="谭佳 portrait"><div><span>校内名师</span><h3>谭佳</h3><p>旅游管理系副教授，聚焦旅游技能人才培养、数智赋能课程建设等教学教改方向。</p></div></div>
<div class="stat-grid"><div class="stat"><strong>10+</strong><span>省部级、市厅级项目</span><p>主持并推进多项教学教改与社会服务项目。</p></div><div class="stat"><strong>10000+</strong><span>课程覆盖人次</span><p>开发《乡村旅游导览实务》等培训课程。</p></div><div class="stat"><strong>30+</strong><span>团队课题</span><p>围绕生态旅游、红色讲解、研学旅游开发等方向开展研究。</p></div></div>
<h2>教学与产业服务成果</h2><ul><li>获全国教师教学能力大赛三等奖、省赛一等奖。</li><li>实践成果入选文旅部优秀成果并在全国推广。</li><li>教学案例入选文旅部旅游职业教育“五金”数智化建设典型案例。</li></ul>
<div class="photo-strip"><figure><img src="{media['image32']}" alt="论坛发言"><figcaption>在论坛活动中进行主旨发言</figcaption></figure><figure><img src="{media['image30']}" alt="校园成果展示"><figcaption>职业教育成果面向行业与社会展示</figcaption></figure></div>
<blockquote>通过老带新、师带徒，优化人才结构，赋能贵州文旅产业高质量发展。</blockquote>
""".strip()


def main() -> None:
    media = extract_media()
    updated_at = now_iso()
    display_config = {
        "logoImageUrl": "",
        "schoolName": "毕节职业技术学院",
        "schoolMeta": "社会服务 · 国际交流 · 育人成果 · 名师名匠",
        "badgeText": "成果展示样例",
        "summaryLabel": "BIJIE VOCATIONAL COLLEGE",
        "summaryTitle": "以 Word 资料为基础，测试后台富文本与大屏展示效果。",
        "summaryCopy": "本方案整理了社会服务、国际交流、优秀毕业生、校内名师四类内容，用指标卡、时间线、图文组合、人物卡片等多种富文本结构做展示样例。",
        "summaryTags": ["富文本", "资料转展示页", "大屏预览", "二维码触发"],
        "scanTitle": "扫描样例二维码",
        "scanCopy": "进入不同编号的展示页，查看富文本标题、列表、图片、引用、时间线和指标卡的展示效果。",
        "scanImageUrl": "",
        "sideTitle": "",
        "sideCopy": "",
        "brandColor": "#28539c",
        "brandDeepColor": "#174275",
        "accent2": "#49c5b6",
        "slides": [
            {
                "label": "社会服务",
                "meta": "SAMPLE 01",
                "title": "服务地方发展",
                "body": "围绕地方产业和乡村振兴需求，展示培训、认定和技术服务成果。",
                "imageUrl": media["image1"],
                "visual": "gate",
            },
            {
                "label": "国际交流",
                "meta": "SAMPLE 02",
                "title": "国际合作成果",
                "body": "展示海外交流、标准输出、多边合作和国际赛事成果。",
                "imageUrl": media["image23"],
                "visual": "library",
            },
            {
                "label": "育人成果",
                "meta": "SAMPLE 03",
                "title": "优秀毕业生",
                "body": "用人物卡片和荣誉标签呈现优秀毕业生成长故事。",
                "imageUrl": media["image37"],
                "visual": "students",
            },
        ],
    }

    pages = [
        {
            "code": "BJ-SERVICE",
            "category": "社会服务成果",
            "source": "毕节职业技术学院",
            "title": "社会服务成果",
            "subtitle": "聚焦技能培训、职业认定与乡村振兴服务，测试指标卡、图文组合与引用块。",
            "body": page_body_social(media),
            "image_url": media["image16"],
            "accent": "#49c5b6",
        },
        {
            "code": "BJ-INTL",
            "category": "国际交流合作",
            "source": "毕节职业技术学院",
            "title": "国际交流合作成果",
            "subtitle": "从海外研学到职业标准输出，测试时间线、列表、图片和分隔线。",
            "body": page_body_international(media),
            "image_url": media["image23"],
            "accent": "#f8c35a",
        },
        {
            "code": "BJ-GRAD",
            "category": "育人成果",
            "source": "教育科学系",
            "title": "优秀毕业生张娅婷",
            "subtitle": "以人物卡片、荣誉标签和分段叙事展示优秀毕业生成长故事。",
            "body": page_body_graduate(media),
            "image_url": media["image37"],
            "accent": "#ff8f5a",
        },
        {
            "code": "BJ-TEACHER",
            "category": "名师名匠",
            "source": "旅游管理系",
            "title": "校内名师谭佳",
            "subtitle": "用人物介绍、数据卡和成果列表展示名师名匠内容模板。",
            "body": page_body_teacher(media),
            "image_url": media["image32"],
            "accent": "#8bd17c",
        },
    ]

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        project = conn.execute(
            "SELECT id FROM projects WHERE name = ?",
            ("毕节职业技术学院成果展示样例",),
        ).fetchone()
        if project:
            project_id = int(project["id"])
            conn.execute(
                """
                UPDATE projects
                SET idle_kicker = ?, idle_title = ?, idle_copy = ?, default_image_url = ?,
                    accent = ?, display_config = ?, deployed = 1, content_deployed = 1, updated_at = ?
                WHERE id = ?
                """,
                (
                    "成果展示样例",
                    "毕节职业技术学院成果展示",
                    "根据资料内容生成的多模板展示页，用于检查后台富文本录入与大屏部署效果。",
                    media["image1"],
                    "#49c5b6",
                    json.dumps(display_config, ensure_ascii=False, separators=(",", ":")),
                    updated_at,
                    project_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO projects (
                    name, idle_kicker, idle_title, idle_copy, welcome_kicker,
                    welcome_title, welcome_subtitle, default_image_url, accent,
                    display_config, deployed, content_deployed, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
                """,
                (
                    "毕节职业技术学院成果展示样例",
                    "成果展示样例",
                    "毕节职业技术学院成果展示",
                    "根据资料内容生成的多模板展示页，用于检查后台富文本录入与大屏部署效果。",
                    "Welcome",
                    "欢迎参观 {title}",
                    "即将进入展示页面",
                    media["image1"],
                    "#49c5b6",
                    json.dumps(display_config, ensure_ascii=False, separators=(",", ":")),
                    updated_at,
                ),
            )
            project_id = int(cursor.lastrowid)

        conn.execute("UPDATE projects SET deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (project_id,))
        conn.execute("UPDATE projects SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (project_id,))

        for page in pages:
            existing = conn.execute("SELECT id FROM pages WHERE code = ?", (page["code"],)).fetchone()
            values = (
                project_id,
                page["code"],
                page["category"],
                page["source"],
                "",
                page["title"],
                page["subtitle"],
                page["body"],
                page["image_url"],
                page["accent"],
                1,
                updated_at,
            )
            if existing:
                conn.execute(
                    """
                    UPDATE pages
                    SET project_id = ?, code = ?, category = ?, source = ?, published_at = ?,
                        title = ?, subtitle = ?, body = ?, image_url = ?, accent = ?,
                        enabled = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    values + (int(existing["id"]),),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO pages (
                        project_id, code, category, source, published_at, title, subtitle,
                        body, image_url, accent, enabled, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )

    print(f"Seeded project {project_id} with {len(pages)} pages.")
    for page in pages:
        print(f"/display?project={project_id}&code={page['code']}&preview=detail")


if __name__ == "__main__":
    main()
