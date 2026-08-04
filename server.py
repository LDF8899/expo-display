import base64
import csv
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import threading
import time
import uuid
from http.cookies import SimpleCookie
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from xml.sax.saxutils import escape as xml_escape

from db_backend import DBError, connect_database, database_backend, execute_mysql_schema
from html_sanitizer import sanitize_rich_html
from storage_backend import asset_storage, asset_storage_backend, storage_status


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


def load_env_file(path=None):
    if not path and os.environ.get("DB_PATH") and "DATABASE_BACKEND" not in os.environ:
        return
    env_path = Path(path or os.environ.get("ENV_FILE") or ROOT / ".env")
    if not env_path.is_absolute():
        env_path = ROOT / env_path
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def env_path(name, default):
    value = os.environ.get(name)
    path = Path(value) if value else Path(default)
    return path if path.is_absolute() else ROOT / path


UPLOAD_DIR = env_path("UPLOAD_DIR", "uploads")
DB_PATH = env_path("DB_PATH", "expo.db")
UNITY_MODEL_DIR = UPLOAD_DIR / "unityceshi111"
UNITY_MODEL_HOST = "127.0.0.1"
UNITY_MODEL_PORT = 8080
UNITY_MODEL_URL = f"http://localhost:{UNITY_MODEL_PORT}/"
DATABASE_BACKEND = database_backend()
MYSQL_SCHEMA_PATH = env_path("MYSQL_SCHEMA_PATH", "database/mysql_schema.sql")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = env_int("PORT", 8000)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")
ADMIN_COOKIE = os.environ.get("ADMIN_COOKIE", "expo_admin_session")
ADMIN_SESSION_SECONDS = env_int("ADMIN_SESSION_SECONDS", 12 * 60 * 60)
CSRF_SECRET = os.environ.get("CSRF_SECRET", "")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", PUBLIC_BASE_URL.startswith("https://"))
ALLOW_DEFAULT_ADMIN_PASSWORD = env_bool("ALLOW_DEFAULT_ADMIN_PASSWORD", False)
TRUST_PROXY_HEADERS = env_bool("TRUST_PROXY_HEADERS", False)
ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
MAX_JSON_BYTES = env_int("MAX_JSON_BYTES", 8 * 1024 * 1024)
MAX_UPLOAD_BYTES = env_int("MAX_UPLOAD_BYTES", 5 * 1024 * 1024)
ALLOW_SVG_UPLOADS = env_bool("ALLOW_SVG_UPLOADS", False)
ASSET_KEY_PREFIX = os.environ.get("ASSET_KEY_PREFIX", "").strip().strip("/")
LOGIN_RATE_LIMIT = env_int("LOGIN_RATE_LIMIT", 10)
LOGIN_RATE_WINDOW_SECONDS = env_int("LOGIN_RATE_WINDOW_SECONDS", 5 * 60)
UPLOAD_RATE_LIMIT = env_int("UPLOAD_RATE_LIMIT", 120)
UPLOAD_RATE_WINDOW_SECONDS = env_int("UPLOAD_RATE_WINDOW_SECONDS", 60 * 60)
PASSWORD_MIN_LENGTH = env_int("PASSWORD_MIN_LENGTH", 10)
ALLOW_WEAK_USER_PASSWORDS = env_bool("ALLOW_WEAK_USER_PASSWORDS", False)
PASSWORD_ITERATIONS = 120000
LATEST_SCAN_SECONDS = 10
DEFAULT_PROJECT_NAME = "毕节职业技术学院"
DEFAULT_SAMPLE_CODE = "DEMO-10100043"
DEFAULT_PAGE_CATEGORY = "校园新闻"
DEFAULT_PAGE_SOURCE = "学校展示"
STANDARD_MODULES = [
    {
        "key": "overview",
        "label": "基本情况",
        "description": "定位、沿革、师资、数据",
        "aliases": ("基本情况", "系部介绍", "系部简介", "概况", "概览", "简介"),
    },
    {
        "key": "majors",
        "label": "专业设置",
        "description": "专业群、课程、就业方向",
        "aliases": ("专业设置", "专业", "专业群", "课程", "就业方向"),
    },
    {
        "key": "training",
        "label": "实训基地",
        "description": "实训室、设备、场景",
        "aliases": ("实训基地", "实训", "实践", "基地", "设备"),
    },
    {
        "key": "cooperation",
        "label": "产教融合",
        "description": "校企合作、订单班、共同体",
        "aliases": ("产教融合", "校企合作", "订单班", "共同体", "社会服务"),
    },
    {
        "key": "achievements",
        "label": "教学成果",
        "description": "课程、竞赛、荣誉、育人成效",
        "aliases": ("教学成果", "成果", "竞赛", "荣誉", "育人成果", "名师名匠", "优秀毕业生", "学生"),
    },
    {
        "key": "media",
        "label": "视频资源",
        "description": "宣传片、专业介绍、作品",
        "aliases": ("视频资源", "视频", "宣传片", "作品"),
    },
    {
        "key": "systems",
        "label": "特色系统入口",
        "description": "业务系统、互动平台",
        "aliases": ("特色系统入口", "系统入口", "业务系统", "互动平台", "系统"),
    },
    {
        "key": "resources",
        "label": "特色数字资源",
        "description": "资源库、专题资料、扫码内容",
        "aliases": ("特色数字资源", "数字资源", "资源库", "专题资料", "扫码内容", "专题"),
    },
]
TOPIC_MODULES = [
    {
        "key": "overview",
        "label": "专题概况",
        "description": "专题背景、建设目标、总体介绍",
        "aliases": ("专题概况", "专题简介", "专题介绍", "概况", "简介", "背景", "topicOverview"),
    },
    {
        "key": "majors",
        "label": "专业群布局",
        "description": "专业群、专业方向、课程、就业方向",
        "aliases": ("专业群布局", "专业群", "专业布局", "专业方向", "课程", "就业方向"),
    },
    {
        "key": "training",
        "label": "实训场景",
        "description": "实训基地、实训室、设备、实践教学",
        "aliases": ("实训场景", "实训基地", "实训", "实践教学", "实训室", "设备", "基地"),
    },
    {
        "key": "cooperation",
        "label": "产教协同",
        "description": "校企合作、订单班、共同体、社会服务",
        "aliases": ("产教协同", "产教融合", "校企合作", "订单班", "共同体", "社会服务"),
    },
    {
        "key": "masters",
        "label": "名师名匠",
        "description": "教学名师、技能大师、教师团队",
        "aliases": ("名师名匠", "名师", "名匠", "教师团队", "教学名师", "技能大师", "大师工作室"),
    },
    {
        "key": "alumni",
        "label": "优秀校友",
        "description": "校友人物、成长经历、就业成果",
        "aliases": ("优秀校友", "校友", "毕业生", "优秀毕业生", "就业典型"),
    },
    {
        "key": "students",
        "label": "优秀学生",
        "description": "学生人物、竞赛经历、成长故事",
        "aliases": ("优秀学生", "学生风采", "学生", "成长故事", "技能成才"),
    },
    {
        "key": "achievements",
        "label": "专题成果",
        "description": "教学成果、项目成果、典型案例",
        "aliases": ("专题成果", "教学成果", "项目成果", "成果", "案例", "建设成果", "图文资料", "topicAchievements", "topicGallery"),
    },
    {
        "key": "competitions",
        "label": "技能大赛",
        "description": "赛事、获奖、承办活动、比赛现场",
        "aliases": ("技能大赛", "大赛", "竞赛", "比赛", "赛项", "获奖"),
    },
    {
        "key": "honors",
        "label": "荣誉资质",
        "description": "证书、奖项、资质、认定结果",
        "aliases": ("荣誉资质", "荣誉", "资质", "证书", "奖项", "认定"),
    },
    {
        "key": "media",
        "label": "视频资源",
        "description": "视频、宣传片、访谈、纪实片",
        "aliases": ("视频资源", "视频", "宣传片", "访谈", "纪实片", "topicMedia"),
    },
]
CONTENT_TYPES = [
    {
        "key": "article",
        "label": "普通图文",
        "description": "标题、摘要、正文、图片轮播；适合专题概况及兜底资料",
    },
    {
        "key": "person",
        "label": "人物类",
        "description": "适合名师名匠、优秀校友、优秀学生，图片与人物介绍并列展示",
    },
    {
        "key": "activity",
        "label": "活动类",
        "description": "适合活动、比赛、产教协同，按时间地点、正文和图片组织",
    },
    {
        "key": "honor",
        "label": "荣誉类",
        "description": "适合证书、奖项、资质，证书图片和获奖信息优先展示",
    },
    {
        "key": "achievement",
        "label": "成果类",
        "description": "适合专题成果、项目成果，摘要和关键指标优先展示",
    },
    {
        "key": "scene",
        "label": "场景类",
        "description": "适合实训场景、设备条件、服务课程和开放对象",
    },
    {
        "key": "video",
        "label": "视频类",
        "description": "适合视频资源，播放器或封面为主，下方展示说明",
    },
]
CONTENT_TYPE_KEYS = {item["key"] for item in CONTENT_TYPES}
CONTENT_TYPE_LABELS = {item["key"]: item["label"] for item in CONTENT_TYPES}
MODULE_DEFAULT_CONTENT_TYPES = {
    "training": "scene",
    "cooperation": "activity",
    "masters": "person",
    "alumni": "person",
    "students": "person",
    "achievements": "achievement",
    "competitions": "activity",
    "honors": "honor",
    "media": "video",
}
PORTAL_TYPES = {
    "school": "学校门户",
    "department": "系部门户",
    "topic": "专题门户",
}
BLUEPRINT_PORTALS = [
    {
        "name": DEFAULT_PROJECT_NAME,
        "portal_type": "school",
        "portal_slug": "",
        "summary": "学校总入口，进入各系部和创新育人专题。",
        "image": "/uploads/4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg",
    },
    {
        "name": "工矿建筑系",
        "portal_type": "department",
        "portal_slug": "mining-construction",
        "summary": "智慧矿山、智能制造与现代建造。",
        "image": "/uploads/blueprint/departments/mining-construction/images/img01.webp",
    },
    {
        "name": "财政经济系",
        "portal_type": "department",
        "portal_slug": "finance",
        "summary": "数字商贸、智慧物流与财务实践。",
        "image": "/uploads/blueprint/departments/finance/images/img01.webp",
    },
    {
        "name": "电子信息工程系",
        "portal_type": "department",
        "portal_slug": "information",
        "summary": "人工智能、网络安全与数字技术。",
        "image": "/uploads/blueprint/departments/information/images/img01.webp",
    },
    {
        "name": "医学护理系",
        "portal_type": "department",
        "portal_slug": "medical-nursing",
        "summary": "临床护理、康养服务与急救教育。",
        "image": "/uploads/blueprint/departments/medical-nursing/images/img01.webp",
    },
    {
        "name": "旅游管理系",
        "portal_type": "department",
        "portal_slug": "tourism",
        "summary": "数字文旅、酒店运营与烹饪技艺。",
        "image": "/uploads/blueprint/departments/tourism/images/img01.webp",
    },
    {
        "name": "现代农业",
        "portal_type": "topic",
        "portal_slug": "modern-agriculture",
        "summary": "山地特色农业、乡村振兴与数字化生产服务。",
        "image": "/uploads/4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg",
    },
    {
        "name": "数字文旅",
        "portal_type": "topic",
        "portal_slug": "digital-tourism",
        "summary": "数字文旅、酒店运营、烹饪技艺与服务场景。",
        "image": "/uploads/blueprint/topics/digital-tourism/images/img01.webp",
    },
    {
        "name": "智慧康养",
        "portal_type": "topic",
        "portal_slug": "smart-healthcare",
        "summary": "护理康养、急救教育、健康管理与服务运营。",
        "image": "/uploads/blueprint/departments/medical-nursing/images/img01.webp",
    },
    {
        "name": "财经商贸",
        "portal_type": "topic",
        "portal_slug": "finance-commerce",
        "summary": "数字商贸、电商物流与产教融合。",
        "image": "/uploads/blueprint/topics/finance-commerce/images/img01.webp",
    },
    {
        "name": "数智技术",
        "portal_type": "topic",
        "portal_slug": "digital-intelligence",
        "summary": "人工智能、网络安全、数据应用与跨专业赋能。",
        "image": "/uploads/blueprint/departments/information/images/img01.webp",
    },
    {
        "name": "智慧能源",
        "portal_type": "topic",
        "portal_slug": "smart-energy",
        "summary": "绿色能源、智能开采与化工安全。",
        "image": "/uploads/blueprint/topics/smart-energy/images/img01.webp",
    },
    {
        "name": "智能制造",
        "portal_type": "topic",
        "portal_slug": "smart-manufacturing",
        "summary": "智能装备、新能源汽车与无人机应用。",
        "image": "/uploads/blueprint/topics/smart-manufacturing/images/img01.webp",
    },
    {
        "name": "智慧建造",
        "portal_type": "topic",
        "portal_slug": "smart-construction",
        "summary": "现代建造、工程管理、测绘应用与绿色施工。",
        "image": "/uploads/blueprint/departments/mining-construction/images/img01.webp",
    },
    {
        "name": "同心校园文化",
        "portal_type": "topic",
        "portal_slug": "campus-culture",
        "summary": "同心育人、校园文化、学生成长与服务地方。",
        "image": "/uploads/4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg",
    },
]
MODULE_SETS = {
    "department": STANDARD_MODULES,
    "school": [
        {
            "key": "service",
            "label": "社会服务",
            "description": "技术服务、培训服务、校地合作",
            "aliases": ("社会服务", "技术服务", "培训服务", "乡村振兴", "服务地方", "校地合作", "继续教育"),
        },
        {
            "key": "international",
            "label": "国际交流",
            "description": "国际合作、交流项目、开放办学",
            "aliases": ("国际交流", "国际交流合作", "国际合作", "中外合作", "境外交流", "留学生"),
        },
        {
            "key": "education",
            "label": "育人成果",
            "description": "人才培养、优秀毕业生、竞赛成果",
            "aliases": ("育人成果", "优秀毕业生", "人才培养", "学生成长", "就业创业", "技能大赛", "竞赛成果"),
        },
        {
            "key": "masters",
            "label": "名师名匠",
            "description": "教学名师、技能大师、双师团队",
            "aliases": ("名师名匠", "教师团队", "教学名师", "技能大师", "双师", "大师工作室"),
        },
    ],
    "topic": TOPIC_MODULES,
}


def normalize_portal_type(value):
    text = str(value or "").strip()
    return text if text in PORTAL_TYPES else "department"


def normalize_portal_slug(value):
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def portal_type_label(value):
    return PORTAL_TYPES[normalize_portal_type(value)]


def portal_preview_url(portal_type, portal_slug=""):
    normalized_type = normalize_portal_type(portal_type)
    slug = normalize_portal_slug(portal_slug)
    if normalized_type == "school":
        return "/departments"
    if normalized_type == "topic":
        return f"/topics/{slug}" if slug else "/departments"
    return f"/departments/{slug}" if slug else "/departments"


def html_attr(value):
    return xml_escape(str(value or ""), {'"': "&quot;"})


def module_set_for_portal_type(portal_type):
    return MODULE_SETS[normalize_portal_type(portal_type)]


def module_meta_for_key(module_key, portal_type="department"):
    return next((module for module in module_set_for_portal_type(portal_type) if module["key"] == module_key), None)


def module_public_payload(module):
    return {
        "key": module["key"],
        "label": module["label"],
        "description": module["description"],
        "aliases": list(module.get("aliases", ())),
        "defaultContentType": default_content_type_for_module(module["key"]),
    }


def content_type_public_payload(content_type):
    return {
        "key": content_type["key"],
        "label": content_type["label"],
        "description": content_type["description"],
    }


def normalize_content_type(value, fallback="article"):
    text = str(value or "").strip().lower()
    if text in CONTENT_TYPE_KEYS:
        return text
    return fallback if fallback in CONTENT_TYPE_KEYS else "article"


def default_content_type_for_module(module_key):
    return MODULE_DEFAULT_CONTENT_TYPES.get(str(module_key or "").strip(), "article")


def content_type_label(value):
    return CONTENT_TYPE_LABELS.get(normalize_content_type(value), CONTENT_TYPE_LABELS["article"])


def content_templates_payload():
    return {
        "portalTypes": PORTAL_TYPES,
        "moduleSets": {
            key: [module_public_payload(module) for module in modules]
            for key, modules in MODULE_SETS.items()
        },
        "contentTypes": [content_type_public_payload(item) for item in CONTENT_TYPES],
    }


def lowcode_field(key, label, field_type="text", required=False, mapping="", placeholder="", options=None, default_value=""):
    field = {
        "key": key,
        "label": label,
        "type": field_type,
        "required": bool(required),
        "mapping": mapping,
        "placeholder": placeholder,
        "defaultValue": default_value,
    }
    if options:
        field["options"] = options
    return field


LOWCODE_META_FIELDS = {
    "person": [
        lowcode_field("personName", "姓名", "text", False, "content_item.meta_json.姓名", "人物姓名"),
        lowcode_field("identity", "身份/职务", "text", False, "content_item.meta_json.身份", "教师职务、校友岗位或学生班级"),
        lowcode_field("tags", "荣誉标签", "text", False, "content_item.meta_json.标签", "技能能手、优秀毕业生等"),
        lowcode_field("story", "主要事迹", "textarea", False, "content_item.body_text", "成长经历、代表成果和可展示亮点"),
    ],
    "activity": [
        lowcode_field("eventDate", "时间", "text", False, "content_item.meta_json.时间", "活动或比赛时间"),
        lowcode_field("location", "地点", "text", False, "content_item.meta_json.地点", "举办地点或实践场景"),
        lowcode_field("units", "参与单位", "text", False, "content_item.meta_json.参与单位", "主办、承办或合作单位"),
        lowcode_field("outcome", "活动成效", "textarea", False, "content_item.body_text", "活动过程、学生参与和成果"),
    ],
    "honor": [
        lowcode_field("honorName", "荣誉名称", "text", False, "content_item.meta_json.荣誉名称", "奖项、资质或认定名称"),
        lowcode_field("level", "级别", "text", False, "content_item.meta_json.级别", "国家级、省级、市级、校级等"),
        lowcode_field("year", "年份", "text", False, "content_item.meta_json.年份", "获评或获奖年份"),
        lowcode_field("recipient", "获奖单位/个人", "text", False, "content_item.meta_json.获奖单位或个人", "对应团队或人员"),
        lowcode_field("value", "展示说明", "textarea", False, "content_item.body_text", "荣誉对专业建设或人才培养的价值"),
    ],
    "achievement": [
        lowcode_field("achievementName", "成果名称", "text", False, "content_item.meta_json.成果名称", "项目、课程、案例或建设成果"),
        lowcode_field("period", "建设周期", "text", False, "content_item.meta_json.建设周期", "起止时间或阶段"),
        lowcode_field("team", "参与团队", "text", False, "content_item.meta_json.参与团队", "教师、学生或合作单位"),
        lowcode_field("metrics", "关键指标", "textarea", False, "content_item.meta_json.关键指标", "获奖、立项、服务人数等数据"),
        lowcode_field("value", "成果价值", "textarea", False, "content_item.body_text", "成果如何支撑人才培养、专业建设或服务地方"),
    ],
    "scene": [
        lowcode_field("sceneName", "场景名称", "text", False, "content_item.meta_json.场景名称", "实训室、基地或设备名称"),
        lowcode_field("positioning", "功能定位", "text", False, "content_item.meta_json.功能定位", "服务课程、训练项目和开放对象"),
        lowcode_field("equipment", "设备条件", "textarea", False, "content_item.meta_json.设备条件", "关键设备、软件平台或工位数量"),
        lowcode_field("application", "教学应用", "textarea", False, "content_item.body_text", "支撑课程教学、技能训练或社会培训的方式"),
    ],
    "video": [
        lowcode_field("duration", "视频时长", "text", False, "content_item.meta_json.视频时长", "如 02:30"),
        lowcode_field("videoUrl", "视频地址", "text", False, "content_item.assets.video", "视频文件地址或外部链接"),
        lowcode_field("scenario", "适用场景", "text", False, "content_item.meta_json.适用场景", "宣传片、访谈、课堂展示或纪实片"),
        lowcode_field("intro", "内容简介", "textarea", False, "content_item.body_text", "概括视频重点"),
    ],
    "article": [
        lowcode_field("bodyText", "正文内容", "textarea", False, "content_item.body_text", "按短段落填写，一段一行或空行分隔"),
    ],
}


def lowcode_schema_for_module(portal_type, module):
    content_type = default_content_type_for_module(module["key"])
    fields = [
        lowcode_field("title", "资料标题", "text", True, "content_item.title", f"{module['label']}标题"),
        lowcode_field("subtitle", "副标题/身份信息", "text", False, "content_item.subtitle", module.get("description", "")),
        lowcode_field("summary", "卡片摘要", "textarea", True, "content_item.summary", "用于门户卡片和抽屉开头，建议 40 到 100 字"),
    ]
    fields.extend(LOWCODE_META_FIELDS.get(content_type, LOWCODE_META_FIELDS["article"]))
    fields.extend(
        [
            lowcode_field("sortOrder", "排序", "number", False, "content_item.sort_order", "数字越小越靠前"),
            lowcode_field("featured", "重点展示", "checkbox", False, "content_item.featured", ""),
            lowcode_field("assets", "图片/视频素材", "asset_list", False, "content_item.assets.gallery", "可上传、从素材库选择，或一行一个素材地址"),
        ]
    )
    return {
        "portalType": normalize_portal_type(portal_type),
        "moduleKey": module["key"],
        "moduleLabel": module["label"],
        "contentType": content_type,
        "contentTypeLabel": content_type_label(content_type),
        "fields": fields,
        "mapping": {
            "target": "content_items",
            "moduleKey": module["key"],
            "contentType": content_type,
        },
    }


def builtin_lowcode_forms():
    forms = []
    for portal_type, modules in MODULE_SETS.items():
        for module in modules:
            content_type = default_content_type_for_module(module["key"])
            portal_label = PORTAL_TYPES.get(portal_type, "门户")
            code = f"LC-{portal_type.upper()}-{module['key'].upper()}"
            forms.append(
                {
                    "name": f"{module['label']}采集表",
                    "code": code,
                    "description": f"{portal_label} · {module['description']}。按模板填写后自动生成结构化资料。",
                    "targetType": "content_item",
                    "targetPortalType": portal_type,
                    "targetContentType": content_type,
                    "targetModuleKey": module["key"],
                    "schema": lowcode_schema_for_module(portal_type, module),
                }
            )
    return forms


DEFAULT_DISPLAY_CONFIG = {
    "logoImageUrl": "",
    "schoolName": DEFAULT_PROJECT_NAME,
    "schoolMeta": "欢迎来到校园 · 同心特色校园文化",
    "badgeText": "欢迎到校",
    "summaryLabel": "WELCOME OVERVIEW",
    "summaryTitle": "从学校形象到展项内容，形成完整参观动线。",
    "summaryCopy": "新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。",
    "summaryTags": ["远距可读", "实时扫码", "项目部署"],
    "scanTitle": "扫描展项二维码",
    "scanCopy": "大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。",
    "scanImageUrl": "",
    "sideTitle": "",
    "sideCopy": "",
    "brandColor": "#28539c",
    "brandDeepColor": "#20468b",
    "accent2": "#47b7ff",
    "slides": [
        {
            "label": "校园入口与主楼",
            "meta": "WELCOME 01",
            "title": "学校形象",
            "body": "用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。",
            "imageUrl": "",
            "visual": "gate",
        },
        {
            "label": "扫码内容导览",
            "meta": "WELCOME 02",
            "title": "成果导览",
            "body": "观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。",
            "imageUrl": "",
            "visual": "library",
        },
        {
            "label": "现场节奏",
            "meta": "WELCOME 03",
            "title": "现场节奏",
            "body": "自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。",
            "imageUrl": "",
            "visual": "students",
        },
    ],
}

SSE_CLIENTS = set()
UNITY_MODEL_PROCESS = None
UNITY_MODEL_LOCK = threading.Lock()
LAST_SCAN = None
RATE_LIMITS = {}
RATE_LIMIT_LOCK = threading.Lock()
WEAK_ONLINE_SECRETS = {
    "",
    "123456",
    "password",
    "admin",
    "change-this-password",
    "change-this-random-csrf-secret",
    "replace-admin-password",
    "replace-random-csrf-secret",
    "REPLACE_WITH_STRONG_ADMIN_PASSWORD",
    "REPLACE_WITH_RANDOM_CSRF_SECRET",
}
WEAK_USER_PASSWORDS = WEAK_ONLINE_SECRETS | {
    "000000",
    "111111",
    "654321",
    "qwerty",
    "abc123",
    "password123",
    "admin123",
    "teacher",
    "teacher123",
    "user",
    "user123",
    "test",
    "test123",
}

UPLOAD_MIME_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}
if ALLOW_SVG_UPLOADS:
    UPLOAD_MIME_EXTENSIONS["image/svg+xml"] = ".svg"


class RequestRejected(Exception):
    pass

QR_L_CAPACITY = {
    1: (19, 7),
    2: (34, 10),
    3: (55, 15),
    4: (80, 20),
    5: (108, 26),
}

QR_ALIGNMENT = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
}

GF_EXP = [0] * 512
GF_LOG = [0] * 256


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def online_mode_enabled():
    return bool(
        PUBLIC_BASE_URL
        or HOST in {"0.0.0.0", "::"}
        or DATABASE_BACKEND == "mysql"
        or asset_storage_backend() != "local"
    )


def validate_runtime_config():
    if not online_mode_enabled():
        return
    if ADMIN_PASSWORD in WEAK_ONLINE_SECRETS and not ALLOW_DEFAULT_ADMIN_PASSWORD:
        raise RuntimeError(
            "线上模式下 ADMIN_PASSWORD 必须是强随机值；仅临时测试时可设置 ALLOW_DEFAULT_ADMIN_PASSWORD=1"
        )
    if CSRF_SECRET in WEAK_ONLINE_SECRETS:
        raise RuntimeError("线上模式下 CSRF_SECRET 必须是强随机值")


def csrf_secret():
    return (CSRF_SECRET or f"{ADMIN_PASSWORD}:{ADMIN_COOKIE}").encode("utf-8")


def csrf_token_for_session(token):
    if not token:
        return ""
    return hmac.new(csrf_secret(), str(token).encode("utf-8"), hashlib.sha256).hexdigest()


def validate_user_password(password, username="", display_name="", required=True):
    password = str(password or "").strip()
    if not password:
        if required:
            raise ValueError("password 不能为空")
        return ""
    if ALLOW_WEAK_USER_PASSWORDS:
        return password
    min_length = max(1, PASSWORD_MIN_LENGTH)
    if len(password) < min_length:
        raise ValueError(f"password 至少需要 {min_length} 个字符")
    lowered = password.lower()
    if lowered in {item.lower() for item in WEAK_USER_PASSWORDS}:
        raise ValueError("password 强度太弱")
    for label, value in (("username", username), ("displayName", display_name)):
        value = str(value or "").strip().lower()
        if value and lowered == value:
            raise ValueError(f"password 不能和 {label} 相同")
    groups = [
        bool(re.search(r"[a-z]", password)),
        bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"\d", password)),
        bool(re.search(r"[^A-Za-z0-9]", password)),
    ]
    if sum(groups) < 2:
        raise ValueError("password 至少需要包含两类字符")
    return password


def rate_limit_retry_after(bucket, key, limit, window_seconds):
    if limit <= 0 or window_seconds <= 0:
        return 0
    now = time.time()
    store_key = f"{bucket}:{key}"
    with RATE_LIMIT_LOCK:
        events = [ts for ts in RATE_LIMITS.get(store_key, []) if ts > now - window_seconds]
        if len(events) >= limit:
            RATE_LIMITS[store_key] = events
            return max(1, int(window_seconds - (now - events[0])) + 1)
        events.append(now)
        RATE_LIMITS[store_key] = events
    return 0


def database_status():
    try:
        with db_connect() as conn:
            row = conn.execute("SELECT 1 AS ok").fetchone()
        return {"ok": bool(row), "backend": DATABASE_BACKEND}
    except Exception as exc:
        return {"ok": False, "backend": DATABASE_BACKEND, "error": str(exc)}


def ready_status():
    checks = {
        "database": database_status(),
        "storage": storage_status(UPLOAD_DIR),
        "runtime": {
            "ok": True,
            "onlineMode": online_mode_enabled(),
            "host": HOST,
            "publicBaseUrl": PUBLIC_BASE_URL,
            "secureCookie": SESSION_COOKIE_SECURE,
            "trustProxyHeaders": TRUST_PROXY_HEADERS,
        },
    }
    ok = all(item.get("ok") for item in checks.values())
    return {
        "ok": ok,
        "time": now_iso(),
        "checks": checks,
    }


def db_connect():
    return connect_database(DB_PATH)


def table_exists(conn, name):
    if DATABASE_BACKEND == "mysql":
        return bool(
            conn.execute(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = ?
                """,
                (name,),
            ).fetchone()
        )
    return bool(
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (name,),
        ).fetchone()
    )


def table_columns(conn, name):
    if not table_exists(conn, name):
        return []
    if DATABASE_BACKEND == "mysql":
        return [
            row["COLUMN_NAME"]
            for row in conn.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = ?
                ORDER BY ORDINAL_POSITION
                """,
                (name,),
            ).fetchall()
        ]
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({name})")]


def drop_index_if_exists(conn, name):
    if DATABASE_BACKEND == "mysql":
        return
    conn.execute(f"DROP INDEX IF EXISTS {name}")


def upsert_admin_credentials(conn):
    if DATABASE_BACKEND == "mysql":
        conn.execute(
            """
            INSERT INTO admin_users (username, password_hash, updated_at)
            VALUES (?, ?, ?)
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                updated_at = VALUES(updated_at)
            """,
            (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD), now_iso()),
        )
        return
    conn.execute(
        """
        INSERT INTO admin_users (username, password_hash, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            password_hash = excluded.password_hash,
            updated_at = excluded.updated_at
        """,
        (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD), now_iso()),
    )


def init_db():
    UPLOAD_DIR.mkdir(exist_ok=True)
    if DATABASE_BACKEND == "mysql":
        init_mysql_db()
        return
    with db_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'teacher',
                department TEXT NOT NULL DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_sessions (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                portal_type TEXT NOT NULL DEFAULT 'department',
                portal_slug TEXT NOT NULL DEFAULT '',
                idle_kicker TEXT NOT NULL DEFAULT '学校简介',
                idle_title TEXT NOT NULL DEFAULT '欢迎来到毕节职业技术学院',
                idle_copy TEXT NOT NULL DEFAULT '毕节职业技术学院立足地方发展需求，围绕人才培养、技术技能教育、社会服务与校园文化建设，打造开放、务实、富有活力的学习共同体。',
                welcome_kicker TEXT NOT NULL DEFAULT 'Welcome',
                welcome_title TEXT NOT NULL DEFAULT '欢迎参观 {title}',
                welcome_subtitle TEXT NOT NULL DEFAULT '即将进入展示页面',
                default_image_url TEXT NOT NULL DEFAULT '/static/expo-stage.png',
                accent TEXT NOT NULL DEFAULT '#f59a13',
                display_config TEXT NOT NULL DEFAULT '{}',
                deployed INTEGER NOT NULL DEFAULT 0,
                content_deployed INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            )
            """
        )
        migrate_projects_table(conn)
        ensure_default_project(conn)
        upgrade_legacy_default_project(conn)
        migrate_pages_table(conn)
        ensure_page_extra_columns(conn)
        ensure_unique_page_codes(conn)
        migrate_role_tables(conn)
        migrate_review_tables(conn)
        ensure_blueprint_portal_projects(conn)
        ensure_blueprint_pages(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                raw_url TEXT NOT NULL,
                project_id INTEGER NOT NULL DEFAULT 0,
                result TEXT NOT NULL DEFAULT 'ok',
                detail TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        migrate_scans_table(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT '',
                action TEXT NOT NULL,
                target_type TEXT NOT NULL DEFAULT '',
                target_id TEXT NOT NULL DEFAULT '',
                target_label TEXT NOT NULL DEFAULT '',
                detail TEXT NOT NULL DEFAULT '',
                changes TEXT NOT NULL DEFAULT '',
                ip TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        migrate_logs_table(conn)
        migrate_assets_table(conn)
        migrate_content_tables(conn)
        migrate_lowcode_tables(conn)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_created_at ON admin_logs(created_at)")
        project_id = deployed_content_project_id(conn)
        existing = conn.execute(
            "SELECT code FROM pages WHERE code = ?",
            (DEFAULT_SAMPLE_CODE,),
        ).fetchone()
        if not existing:
            conn.execute(
                """
                INSERT INTO pages (project_id, code, title, subtitle, body, image_url, accent, enabled, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (
                    project_id,
                    DEFAULT_SAMPLE_CODE,
                    "欢迎来到成果展示",
                    "深圳先进技术研究院展会互动展示",
                    "这里可以放项目介绍、展品亮点、团队说明和现场引导文案。后台可以随时替换这些文字和图片。",
                    "/static/sample.svg",
                    "#0f766e",
                    now_iso(),
                ),
            )
        upsert_admin_credentials(conn)
        ensure_default_user(conn)
        seed_lowcode_forms(conn)
        ensure_legacy_versions(conn)


def init_mysql_db():
    with db_connect() as conn:
        execute_mysql_schema(conn, MYSQL_SCHEMA_PATH)
        ensure_page_extra_columns(conn)
        migrate_content_tables(conn)
        migrate_lowcode_tables(conn)
        upsert_admin_credentials(conn)
        ensure_default_user(conn)
        seed_lowcode_forms(conn)
        ensure_default_project(conn)
        ensure_blueprint_portal_projects(conn)
        ensure_blueprint_pages(conn)
        project_id = deployed_content_project_id(conn)
        existing = conn.execute(
            "SELECT code FROM pages WHERE code = ?",
            (DEFAULT_SAMPLE_CODE,),
        ).fetchone()
        if not existing:
            conn.execute(
                """
                INSERT INTO pages (
                    project_id, code, title, subtitle, body, image_url, accent,
                    enabled, review_status, submitted_by, reviewed_by, review_note, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'approved', ?, ?, '', ?)
                """,
                (
                    project_id,
                    DEFAULT_SAMPLE_CODE,
                    "欢迎来到成果展示",
                    "深圳先进技术研究院展会互动展示",
                    "这里可以放项目介绍、展品亮点、团队说明和现场引导文案。后台可以随时替换这些文字和图片。",
                    "/static/sample.svg",
                    "#0f766e",
                    ADMIN_USERNAME,
                    ADMIN_USERNAME,
                    now_iso(),
                ),
            )
        ensure_legacy_versions(conn)


def ensure_default_project(conn):
    if conn.execute("SELECT id FROM projects LIMIT 1").fetchone():
        if not conn.execute("SELECT id FROM projects WHERE deployed = 1 LIMIT 1").fetchone():
            first = conn.execute("SELECT id FROM projects WHERE portal_type = 'school' ORDER BY id LIMIT 1").fetchone()
            if not first:
                first = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
            conn.execute("UPDATE projects SET deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (first["id"],))
        if not conn.execute("SELECT id FROM projects WHERE content_deployed = 1 LIMIT 1").fetchone():
            first = conn.execute("SELECT id FROM projects WHERE deployed = 1 ORDER BY id LIMIT 1").fetchone()
            if not first:
                first = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
            conn.execute("UPDATE projects SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (first["id"],))
        return

    conn.execute(
        """
        INSERT INTO projects (
            name, portal_type, idle_kicker, idle_title, idle_copy, welcome_kicker,
            welcome_title, welcome_subtitle, default_image_url, accent, display_config,
            deployed, content_deployed, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
        """,
        (
            DEFAULT_PROJECT_NAME,
            "school",
            "学校简介",
            "欢迎来到毕节职业技术学院",
            "毕节职业技术学院立足地方发展需求，围绕人才培养、技术技能教育、社会服务与校园文化建设，打造开放、务实、富有活力的学习共同体。",
            "Welcome",
            "欢迎参观 {title}",
            "即将进入展示页面",
            "/static/expo-stage.png",
            "#f59a13",
            display_config_json(DEFAULT_DISPLAY_CONFIG),
            now_iso(),
        ),
    )


def migrate_projects_table(conn):
    columns = set(table_columns(conn, "projects"))
    if "portal_type" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN portal_type TEXT NOT NULL DEFAULT 'department'")
        conn.execute(
            "UPDATE projects SET portal_type = 'school' WHERE deployed = 1 OR name LIKE ?",
            (f"{DEFAULT_PROJECT_NAME}%",),
        )
    else:
        conn.execute("UPDATE projects SET portal_type = 'department' WHERE portal_type IS NULL OR portal_type = ''")
    columns = set(table_columns(conn, "projects"))
    if "portal_slug" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN portal_slug VARCHAR(160) NOT NULL DEFAULT ''")
        conn.execute("UPDATE projects SET portal_slug = '' WHERE portal_type = 'school'")
        for portal in BLUEPRINT_PORTALS:
            if portal["portal_type"] == "school":
                continue
            conn.execute(
                "UPDATE projects SET portal_slug = ? WHERE portal_type = ? AND name = ? AND portal_slug = ''",
                (portal["portal_slug"], portal["portal_type"], portal["name"]),
            )
    if "display_config" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN display_config TEXT NOT NULL DEFAULT '{}'")
    if "content_deployed" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN content_deployed INTEGER NOT NULL DEFAULT 0")
        conn.execute("UPDATE projects SET content_deployed = deployed")


def upgrade_legacy_default_project(conn):
    legacy = conn.execute(
        """
        SELECT id
        FROM projects
        WHERE name = ?
          AND idle_kicker = ?
          AND idle_title = ?
          AND idle_copy = ?
          AND accent = ?
        """,
        ("默认展会", "Achievement Expo", "成果展示互动屏", "请扫描展品二维码", "#0f766e"),
    ).fetchall()
    for row in legacy:
        conn.execute(
            """
            UPDATE projects SET
                name = ?,
                portal_type = 'school',
                idle_kicker = ?,
                idle_title = ?,
                idle_copy = ?,
                accent = ?,
                display_config = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                DEFAULT_PROJECT_NAME,
                "学校简介",
                "欢迎来到毕节职业技术学院",
                DEFAULT_DISPLAY_CONFIG["summaryCopy"],
                "#f59a13",
                display_config_json(DEFAULT_DISPLAY_CONFIG),
                now_iso(),
                row["id"],
            ),
        )


def ensure_blueprint_portal_projects(conn):
    conn.execute("UPDATE projects SET portal_slug = '' WHERE portal_slug IS NULL")
    conn.execute("UPDATE projects SET portal_slug = '' WHERE portal_type = 'school'")
    for portal in BLUEPRINT_PORTALS:
        portal_type = normalize_portal_type(portal["portal_type"])
        portal_slug = "" if portal_type == "school" else normalize_portal_slug(portal["portal_slug"])
        existing = conn.execute(
            """
            SELECT id FROM projects
            WHERE portal_type = ? AND portal_slug = ?
            ORDER BY deployed DESC, content_deployed DESC, id
            LIMIT 1
            """,
            (portal_type, portal_slug),
        ).fetchone()
        if existing:
            continue
        conn.execute(
            """
            INSERT INTO projects (
                name, portal_type, portal_slug, owner_username,
                idle_kicker, idle_title, idle_copy,
                welcome_kicker, welcome_title, welcome_subtitle,
                default_image_url, accent, display_config,
                deployed, content_deployed, config_status, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 'approved', ?)
            """,
            (
                portal["name"],
                portal_type,
                portal_slug,
                ADMIN_USERNAME,
                portal_type_label(portal_type),
                portal["name"],
                portal["summary"],
                "Welcome",
                "欢迎参观 {title}",
                "即将进入展示页面",
                portal["image"] or "/static/expo-stage.png",
                "#49c5b6" if portal_type == "school" else "#f59a13",
                display_config_json(DEFAULT_DISPLAY_CONFIG if portal_type == "school" else {}),
                now_iso(),
            ),
        )


def blueprint_data_path(portal_type, portal_slug):
    if normalize_portal_type(portal_type) == "topic":
        return STATIC_DIR / "blueprint" / "data" / "topics" / f"{portal_slug}.json"
    return STATIC_DIR / "blueprint" / "data" / "departments" / f"{portal_slug}.json"


def load_blueprint_json(portal_type, portal_slug):
    path = blueprint_data_path(portal_type, portal_slug)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def blueprint_section_category(portal_type, section):
    section_id = str(section.get("id") or "").strip()
    title = str(section.get("title") or "").strip()
    if normalize_portal_type(portal_type) == "topic":
        if section_id == "overview":
            return "专题概况"
        if section_id in {"achievements", "competitions", "honors"}:
            return "专题成果"
        if section_id == "media":
            return "视频资源"
        return "图文资料"
    aliases = {
        "overview": "基本情况",
        "majors": "专业设置",
        "training": "实训基地",
        "cooperation": "产教融合",
        "achievements": "教学成果",
        "media": "视频资源",
        "systems": "特色系统入口",
        "resources": "特色数字资源",
    }
    return aliases.get(section_id) or title or "基本情况"


def blueprint_blocks_to_html(blocks):
    parts = []
    for block in blocks or []:
        block_type = block.get("type")
        if block_type == "text":
            text = str(block.get("content") or "").strip()
            if text:
                parts.append(f"<p>{xml_escape(text)}</p>")
        elif block_type == "image":
            src = str(block.get("src") or "").strip()
            caption = str(block.get("caption") or "").strip()
            if src:
                figure = f'<figure><img src="{html_attr(src)}" alt="{html_attr(caption)}">'
                if caption:
                    figure += f"<figcaption>{xml_escape(caption)}</figcaption>"
                figure += "</figure>"
                parts.append(figure)
        elif block_type == "video":
            src = str(block.get("src") or "").strip()
            title = str(block.get("title") or "视频资源").strip()
            poster = str(block.get("poster") or "").strip()
            if src:
                video = f"<figure><p><strong>{xml_escape(title)}</strong></p>"
                if poster:
                    video += f'<img src="{html_attr(poster)}" alt="{html_attr(title)}">'
                video += f'<figcaption><a href="{html_attr(src)}">查看视频资源</a></figcaption></figure>'
                parts.append(video)
    return "\n".join(parts).strip() or "<p>资料待补充。</p>"


def blueprint_first_media(blocks, fallback=""):
    for block in blocks or []:
        if block.get("type") == "image" and block.get("src"):
            return str(block.get("src") or "")
        if block.get("type") == "video" and block.get("poster"):
            return str(block.get("poster") or "")
    return fallback or ""


def blueprint_page_code(portal_type, portal_slug, section_id):
    prefix = "TOPIC" if normalize_portal_type(portal_type) == "topic" else "DEPT"
    slug = normalize_portal_slug(portal_slug).upper().replace("-", "_") or "PORTAL"
    section = normalize_portal_slug(section_id).upper().replace("-", "_") or "SECTION"
    return f"BP-{prefix}-{slug}-{section}"


def ensure_blueprint_pages(conn):
    projects = conn.execute(
        """
        SELECT id, name, portal_type, portal_slug, default_image_url
        FROM projects
        WHERE portal_type IN ('department', 'topic') AND portal_slug <> ''
        ORDER BY id
        """
    ).fetchall()
    now = now_iso()
    for project in projects:
        existing = conn.execute("SELECT id FROM pages WHERE project_id = ? LIMIT 1", (project["id"],)).fetchone()
        if existing:
            continue
        data = load_blueprint_json(project["portal_type"], project["portal_slug"])
        if not data:
            continue
        for index, section in enumerate(data.get("sections") or [], start=1):
            section_id = str(section.get("id") or f"section-{index}").strip()
            blocks = section.get("blocks") or []
            code = unique_page_code(conn, blueprint_page_code(project["portal_type"], project["portal_slug"], section_id))
            category = blueprint_section_category(project["portal_type"], section)
            title = str(section.get("title") or category or data.get("name") or project["name"]).strip()
            body = blueprint_blocks_to_html(blocks)
            image_url = blueprint_first_media(blocks, data.get("cover") or project["default_image_url"])
            content_type = default_content_type_for_module(module_key_for_category(category, project["portal_type"]) or section_id)
            cursor = conn.execute(
                """
                INSERT INTO pages (
                    project_id, code, category, source, published_at, title, subtitle,
                    body, image_url, content_type, accent, enabled, review_status, pending_version_id,
                    submitted_by, reviewed_by, review_note, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'approved', NULL, ?, ?, '', ?)
                """,
                (
                    project["id"],
                    code,
                    category,
                    "蓝图资料同步",
                    now[:10],
                    title,
                    str(data.get("summary") or "").strip(),
                    body,
                    image_url,
                    content_type,
                    "#f59a13",
                    ADMIN_USERNAME,
                    ADMIN_USERNAME,
                    now,
                ),
            )
            snapshot = {
                "code": code,
                "category": category,
                "source": "蓝图资料同步",
                "publishedAt": now[:10],
                "title": title,
                "subtitle": str(data.get("summary") or "").strip(),
                "body": body,
                "imageUrl": image_url,
                "contentType": content_type,
                "accent": "#f59a13",
                "enabled": True,
            }
            conn.execute(
                """
                INSERT INTO page_versions (
                    page_id, project_id, code, operation, status, snapshot,
                    submitted_by, submitted_at, reviewed_by, reviewed_at, changes
                )
                VALUES (?, ?, ?, 'upsert', 'approved', ?, ?, ?, ?, ?, ?)
                """,
                (
                    cursor.lastrowid,
                    project["id"],
                    code,
                    json.dumps(snapshot, ensure_ascii=False),
                    ADMIN_USERNAME,
                    now,
                    ADMIN_USERNAME,
                    now,
                    "blueprint-sync",
                ),
            )


def deployed_project_id(conn=None):
    close_conn = conn is None
    conn = conn or db_connect()
    try:
        row = conn.execute("SELECT id FROM projects WHERE deployed = 1 AND portal_type = 'school' ORDER BY id LIMIT 1").fetchone()
        if row:
            return row["id"]
        row = conn.execute("SELECT id FROM projects WHERE portal_type = 'school' ORDER BY id LIMIT 1").fetchone()
        if row:
            return row["id"]
        row = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
        return row["id"] if row else None
    finally:
        if close_conn:
            conn.close()


def deployed_content_project_id(conn=None):
    close_conn = conn is None
    conn = conn or db_connect()
    try:
        row = conn.execute("SELECT id FROM projects WHERE content_deployed = 1 ORDER BY id LIMIT 1").fetchone()
        if row:
            return row["id"]
        return deployed_project_id(conn)
    finally:
        if close_conn:
            conn.close()


def migrate_pages_table(conn):
    desired = {
        "id",
        "project_id",
        "code",
        "title",
        "subtitle",
        "body",
        "image_url",
        "accent",
        "enabled",
        "updated_at",
    }
    project_id = deployed_content_project_id(conn)

    if not table_exists(conn, "pages"):
        create_pages_table(conn)
        return

    columns = set(table_columns(conn, "pages"))
    if desired.issubset(columns):
        return

    old_rows = conn.execute(
        """
        SELECT code, title, subtitle, body, image_url, accent, enabled, updated_at
        FROM pages
        """
    ).fetchall()
    conn.execute("ALTER TABLE pages RENAME TO pages_old")
    create_pages_table(conn)
    for row in old_rows:
        conn.execute(
            """
            INSERT OR REPLACE INTO pages (
                project_id, code, title, subtitle, body, image_url, accent, enabled, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                row["code"],
                row["title"],
                row["subtitle"],
                row["body"],
                row["image_url"],
                row["accent"],
                row["enabled"],
                row["updated_at"],
            ),
        )
    conn.execute("DROP TABLE pages_old")


def create_pages_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '校园新闻',
            source TEXT NOT NULL DEFAULT '学校展示',
            published_at TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL,
            subtitle TEXT NOT NULL DEFAULT '',
            body TEXT NOT NULL DEFAULT '',
            image_url TEXT NOT NULL DEFAULT '',
            content_type TEXT NOT NULL DEFAULT 'article',
            accent TEXT NOT NULL DEFAULT '#0f766e',
            enabled INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL,
            UNIQUE(project_id, code)
        )
        """
    )


def ensure_page_extra_columns(conn):
    columns = set(table_columns(conn, "pages"))
    if "category" not in columns:
        column_type = "VARCHAR(120)" if DATABASE_BACKEND == "mysql" else "TEXT"
        conn.execute(f"ALTER TABLE pages ADD COLUMN category {column_type} NOT NULL DEFAULT '校园新闻'")
    if "source" not in columns:
        column_type = "VARCHAR(160)" if DATABASE_BACKEND == "mysql" else "TEXT"
        conn.execute(f"ALTER TABLE pages ADD COLUMN source {column_type} NOT NULL DEFAULT '学校展示'")
    if "published_at" not in columns:
        column_type = "VARCHAR(80)" if DATABASE_BACKEND == "mysql" else "TEXT"
        conn.execute(f"ALTER TABLE pages ADD COLUMN published_at {column_type} NOT NULL DEFAULT ''")
    if "content_type" not in columns:
        if DATABASE_BACKEND == "mysql":
            conn.execute("ALTER TABLE pages ADD COLUMN content_type VARCHAR(32) NOT NULL DEFAULT 'article'")
        else:
            conn.execute("ALTER TABLE pages ADD COLUMN content_type TEXT NOT NULL DEFAULT 'article'")


def ensure_unique_page_codes(conn):
    duplicates = conn.execute(
        """
        SELECT code, GROUP_CONCAT(id) AS ids
        FROM pages
        GROUP BY code
        HAVING COUNT(*) > 1
        """
    ).fetchall()
    for row in duplicates:
        ids = [int(page_id) for page_id in str(row["ids"]).split(",") if str(page_id).isdigit()]
        for index, page_id in enumerate(ids[1:], start=2):
            new_code = unique_page_code(conn, f"{row['code']}-{index}")
            conn.execute(
                "UPDATE pages SET code = ?, updated_at = ? WHERE id = ?",
                (new_code, now_iso(), page_id),
            )
    drop_index_if_exists(conn, "idx_pages_code_unique")


def unique_page_code(conn, preferred):
    base = str(preferred or "page").strip() or "page"
    code = base
    index = 2
    while conn.execute("SELECT id FROM pages WHERE code = ?", (code,)).fetchone():
        code = f"{base}-{index}"
        index += 1
    return code


def migrate_role_tables(conn):
    project_columns = set(table_columns(conn, "projects"))
    if "owner_username" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN owner_username TEXT NOT NULL DEFAULT 'admin'")
    if "config_status" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN config_status TEXT NOT NULL DEFAULT 'approved'")
    if "pending_config_version_id" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN pending_config_version_id INTEGER")

    page_columns = set(table_columns(conn, "pages"))
    if "review_status" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN review_status TEXT NOT NULL DEFAULT 'approved'")
    if "pending_version_id" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN pending_version_id INTEGER")
    if "submitted_by" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN submitted_by TEXT NOT NULL DEFAULT 'admin'")
    if "reviewed_by" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN reviewed_by TEXT NOT NULL DEFAULT 'admin'")
    if "review_note" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN review_note TEXT NOT NULL DEFAULT ''")


def migrate_review_tables(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS page_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id INTEGER,
            project_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            operation TEXT NOT NULL DEFAULT 'upsert',
            status TEXT NOT NULL DEFAULT 'pending',
            snapshot TEXT NOT NULL,
            submitted_by TEXT NOT NULL DEFAULT '',
            submitted_at TEXT NOT NULL,
            reviewed_by TEXT NOT NULL DEFAULT '',
            reviewed_at TEXT NOT NULL DEFAULT '',
            review_note TEXT NOT NULL DEFAULT '',
            changes TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS project_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            snapshot TEXT NOT NULL,
            submitted_by TEXT NOT NULL DEFAULT '',
            submitted_at TEXT NOT NULL,
            reviewed_by TEXT NOT NULL DEFAULT '',
            reviewed_at TEXT NOT NULL DEFAULT '',
            review_note TEXT NOT NULL DEFAULT '',
            changes TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS deployed_pages (
            project_id INTEGER NOT NULL,
            page_id INTEGER NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id, page_id)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_status ON page_versions(status, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_project_versions_status ON project_versions(status, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_project ON page_versions(project_id, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_page ON page_versions(page_id, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_project_versions_project ON project_versions(project_id, submitted_at)")
    conn.execute("DELETE FROM page_versions WHERE project_id NOT IN (SELECT id FROM projects)")
    conn.execute("DELETE FROM project_versions WHERE project_id NOT IN (SELECT id FROM projects)")


def migrate_scans_table(conn):
    columns = set(table_columns(conn, "scans"))
    if "project_id" not in columns:
        conn.execute("ALTER TABLE scans ADD COLUMN project_id INTEGER NOT NULL DEFAULT 0")
    if "result" not in columns:
        conn.execute("ALTER TABLE scans ADD COLUMN result TEXT NOT NULL DEFAULT 'ok'")
    if "detail" not in columns:
        conn.execute("ALTER TABLE scans ADD COLUMN detail TEXT NOT NULL DEFAULT ''")


def migrate_logs_table(conn):
    columns = set(table_columns(conn, "admin_logs"))
    if "role" not in columns:
        conn.execute("ALTER TABLE admin_logs ADD COLUMN role TEXT NOT NULL DEFAULT ''")
    if "changes" not in columns:
        conn.execute("ALTER TABLE admin_logs ADD COLUMN changes TEXT NOT NULL DEFAULT ''")


def migrate_assets_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_username TEXT NOT NULL DEFAULT '',
            original_filename TEXT NOT NULL DEFAULT '',
            storage_key TEXT NOT NULL,
            url TEXT NOT NULL,
            mime_type TEXT NOT NULL DEFAULT '',
            size_bytes INTEGER NOT NULL DEFAULT 0,
            backend TEXT NOT NULL DEFAULT 'local',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_owner_created ON assets(owner_username, created_at)")


def migrate_content_tables(conn):
    if DATABASE_BACKEND == "mysql":
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_items (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              project_id BIGINT NOT NULL,
              page_id BIGINT NULL,
              code VARCHAR(160) NOT NULL,
              module_key VARCHAR(80) NOT NULL,
              content_type VARCHAR(32) NOT NULL DEFAULT 'article',
              title VARCHAR(255) NOT NULL,
              subtitle VARCHAR(512) NOT NULL DEFAULT '',
              summary VARCHAR(1024) NOT NULL DEFAULT '',
              body_json JSON NOT NULL,
              meta_json JSON NOT NULL,
              cover_asset_id BIGINT NULL,
              sort_order INT NOT NULL DEFAULT 0,
              featured TINYINT(1) NOT NULL DEFAULT 0,
              enabled TINYINT(1) NOT NULL DEFAULT 1,
              review_status VARCHAR(32) NOT NULL DEFAULT 'approved',
              pending_version_id BIGINT NULL,
              submitted_by VARCHAR(64) NOT NULL DEFAULT 'admin',
              reviewed_by VARCHAR(64) NOT NULL DEFAULT 'admin',
              review_note VARCHAR(1024) NOT NULL DEFAULT '',
              created_at VARCHAR(40) NOT NULL,
              updated_at VARCHAR(40) NOT NULL,
              UNIQUE KEY uq_content_items_project_code (project_id, code),
              INDEX idx_content_items_project_module (project_id, module_key, sort_order),
              INDEX idx_content_items_project_status (project_id, review_status),
              INDEX idx_content_items_type (content_type),
              CONSTRAINT fk_content_items_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
              CONSTRAINT fk_content_items_page FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE SET NULL,
              CONSTRAINT fk_content_items_cover FOREIGN KEY (cover_asset_id) REFERENCES assets(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_item_assets (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              content_item_id BIGINT NOT NULL,
              asset_id BIGINT NULL,
              role VARCHAR(40) NOT NULL DEFAULT 'gallery',
              title VARCHAR(255) NOT NULL DEFAULT '',
              caption VARCHAR(512) NOT NULL DEFAULT '',
              url VARCHAR(2048) NOT NULL DEFAULT '',
              sort_order INT NOT NULL DEFAULT 0,
              created_at VARCHAR(40) NOT NULL,
              INDEX idx_content_item_assets_item (content_item_id, sort_order),
              INDEX idx_content_item_assets_asset (asset_id),
              CONSTRAINT fk_content_item_assets_item FOREIGN KEY (content_item_id) REFERENCES content_items(id) ON DELETE CASCADE,
              CONSTRAINT fk_content_item_assets_asset FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS content_item_versions (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              content_item_id BIGINT NULL,
              project_id BIGINT NOT NULL,
              operation VARCHAR(32) NOT NULL DEFAULT 'upsert',
              status VARCHAR(32) NOT NULL DEFAULT 'pending',
              snapshot_json JSON NOT NULL,
              submitted_by VARCHAR(64) NOT NULL DEFAULT '',
              submitted_at VARCHAR(40) NOT NULL,
              reviewed_by VARCHAR(64) NOT NULL DEFAULT '',
              reviewed_at VARCHAR(40) NOT NULL DEFAULT '',
              review_note VARCHAR(1024) NOT NULL DEFAULT '',
              changes VARCHAR(2048) NOT NULL DEFAULT '',
              INDEX idx_content_item_versions_status (status, submitted_at),
              INDEX idx_content_item_versions_project (project_id),
              INDEX idx_content_item_versions_item (content_item_id),
              CONSTRAINT fk_content_item_versions_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
              CONSTRAINT fk_content_item_versions_item FOREIGN KEY (content_item_id) REFERENCES content_items(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        return

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            page_id INTEGER,
            code TEXT NOT NULL,
            module_key TEXT NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'article',
            title TEXT NOT NULL,
            subtitle TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '',
            body_json TEXT NOT NULL,
            meta_json TEXT NOT NULL,
            cover_asset_id INTEGER,
            sort_order INTEGER NOT NULL DEFAULT 0,
            featured INTEGER NOT NULL DEFAULT 0,
            enabled INTEGER NOT NULL DEFAULT 1,
            review_status TEXT NOT NULL DEFAULT 'approved',
            pending_version_id INTEGER,
            submitted_by TEXT NOT NULL DEFAULT 'admin',
            reviewed_by TEXT NOT NULL DEFAULT 'admin',
            review_note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(project_id, code)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS content_item_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_item_id INTEGER NOT NULL,
            asset_id INTEGER,
            role TEXT NOT NULL DEFAULT 'gallery',
            title TEXT NOT NULL DEFAULT '',
            caption TEXT NOT NULL DEFAULT '',
            url TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS content_item_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_item_id INTEGER,
            project_id INTEGER NOT NULL,
            operation TEXT NOT NULL DEFAULT 'upsert',
            status TEXT NOT NULL DEFAULT 'pending',
            snapshot_json TEXT NOT NULL,
            submitted_by TEXT NOT NULL DEFAULT '',
            submitted_at TEXT NOT NULL,
            reviewed_by TEXT NOT NULL DEFAULT '',
            reviewed_at TEXT NOT NULL DEFAULT '',
            review_note TEXT NOT NULL DEFAULT '',
            changes TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_content_items_project_module ON content_items(project_id, module_key, sort_order)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_content_items_project_status ON content_items(project_id, review_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_content_item_assets_item ON content_item_assets(content_item_id, sort_order)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_content_item_versions_status ON content_item_versions(status, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_content_item_versions_project ON content_item_versions(project_id, submitted_at)")


def migrate_lowcode_tables(conn):
    if DATABASE_BACKEND == "mysql":
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lowcode_forms (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              name VARCHAR(255) NOT NULL,
              code VARCHAR(120) NOT NULL,
              description VARCHAR(1024) NOT NULL DEFAULT '',
              target_type VARCHAR(40) NOT NULL DEFAULT 'content_item',
              target_portal_type VARCHAR(40) NOT NULL DEFAULT 'department',
              target_content_type VARCHAR(32) NOT NULL DEFAULT 'article',
              target_module_key VARCHAR(80) NOT NULL DEFAULT '',
              enabled TINYINT(1) NOT NULL DEFAULT 1,
              created_by VARCHAR(64) NOT NULL DEFAULT 'system',
              created_at VARCHAR(40) NOT NULL,
              updated_at VARCHAR(40) NOT NULL,
              UNIQUE KEY uq_lowcode_forms_code (code),
              INDEX idx_lowcode_forms_target (target_portal_type, target_module_key, enabled)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lowcode_form_versions (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              form_id BIGINT NOT NULL,
              version_no INT NOT NULL DEFAULT 1,
              schema_json JSON NOT NULL,
              status VARCHAR(32) NOT NULL DEFAULT 'active',
              created_by VARCHAR(64) NOT NULL DEFAULT 'system',
              created_at VARCHAR(40) NOT NULL,
              UNIQUE KEY uq_lowcode_form_versions_form_version (form_id, version_no),
              INDEX idx_lowcode_form_versions_form_status (form_id, status),
              CONSTRAINT fk_lowcode_form_versions_form
                FOREIGN KEY (form_id) REFERENCES lowcode_forms(id)
                ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lowcode_records (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              form_id BIGINT NOT NULL,
              form_version_id BIGINT NOT NULL,
              project_id BIGINT NOT NULL,
              content_item_id BIGINT NULL,
              status VARCHAR(32) NOT NULL DEFAULT 'pending',
              data_json JSON NOT NULL,
              submitted_by VARCHAR(64) NOT NULL DEFAULT '',
              submitted_at VARCHAR(40) NOT NULL,
              reviewed_by VARCHAR(64) NOT NULL DEFAULT '',
              reviewed_at VARCHAR(40) NOT NULL DEFAULT '',
              review_note VARCHAR(1024) NOT NULL DEFAULT '',
              created_at VARCHAR(40) NOT NULL,
              updated_at VARCHAR(40) NOT NULL,
              INDEX idx_lowcode_records_project (project_id, submitted_at),
              INDEX idx_lowcode_records_form (form_id, submitted_at),
              INDEX idx_lowcode_records_content_item (content_item_id),
              CONSTRAINT fk_lowcode_records_form
                FOREIGN KEY (form_id) REFERENCES lowcode_forms(id)
                ON DELETE RESTRICT,
              CONSTRAINT fk_lowcode_records_version
                FOREIGN KEY (form_version_id) REFERENCES lowcode_form_versions(id)
                ON DELETE RESTRICT,
              CONSTRAINT fk_lowcode_records_project
                FOREIGN KEY (project_id) REFERENCES projects(id)
                ON DELETE CASCADE,
              CONSTRAINT fk_lowcode_records_content_item
                FOREIGN KEY (content_item_id) REFERENCES content_items(id)
                ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lowcode_record_assets (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              record_id BIGINT NOT NULL,
              asset_id BIGINT NULL,
              role VARCHAR(40) NOT NULL DEFAULT 'gallery',
              title VARCHAR(255) NOT NULL DEFAULT '',
              caption VARCHAR(512) NOT NULL DEFAULT '',
              url VARCHAR(2048) NOT NULL DEFAULT '',
              sort_order INT NOT NULL DEFAULT 0,
              created_at VARCHAR(40) NOT NULL,
              INDEX idx_lowcode_record_assets_record (record_id, sort_order),
              CONSTRAINT fk_lowcode_record_assets_record
                FOREIGN KEY (record_id) REFERENCES lowcode_records(id)
                ON DELETE CASCADE,
              CONSTRAINT fk_lowcode_record_assets_asset
                FOREIGN KEY (asset_id) REFERENCES assets(id)
                ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        return

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lowcode_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            target_type TEXT NOT NULL DEFAULT 'content_item',
            target_portal_type TEXT NOT NULL DEFAULT 'department',
            target_content_type TEXT NOT NULL DEFAULT 'article',
            target_module_key TEXT NOT NULL DEFAULT '',
            enabled INTEGER NOT NULL DEFAULT 1,
            created_by TEXT NOT NULL DEFAULT 'system',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lowcode_form_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            version_no INTEGER NOT NULL DEFAULT 1,
            schema_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_by TEXT NOT NULL DEFAULT 'system',
            created_at TEXT NOT NULL,
            UNIQUE(form_id, version_no)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lowcode_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            form_version_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            content_item_id INTEGER,
            status TEXT NOT NULL DEFAULT 'pending',
            data_json TEXT NOT NULL,
            submitted_by TEXT NOT NULL DEFAULT '',
            submitted_at TEXT NOT NULL,
            reviewed_by TEXT NOT NULL DEFAULT '',
            reviewed_at TEXT NOT NULL DEFAULT '',
            review_note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lowcode_record_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            asset_id INTEGER,
            role TEXT NOT NULL DEFAULT 'gallery',
            title TEXT NOT NULL DEFAULT '',
            caption TEXT NOT NULL DEFAULT '',
            url TEXT NOT NULL DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lowcode_forms_target ON lowcode_forms(target_portal_type, target_module_key, enabled)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lowcode_form_versions_form_status ON lowcode_form_versions(form_id, status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lowcode_records_project ON lowcode_records(project_id, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lowcode_records_form ON lowcode_records(form_id, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lowcode_records_content_item ON lowcode_records(content_item_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lowcode_record_assets_record ON lowcode_record_assets(record_id, sort_order)")


def seed_lowcode_forms(conn):
    now = now_iso()
    for form in builtin_lowcode_forms():
        existing = conn.execute("SELECT id FROM lowcode_forms WHERE code = ?", (form["code"],)).fetchone()
        if DATABASE_BACKEND == "mysql":
            conn.execute(
                """
                INSERT INTO lowcode_forms (
                    name, code, description, target_type, target_portal_type,
                    target_content_type, target_module_key, enabled, created_by,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'system', ?, ?)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    description = VALUES(description),
                    target_type = VALUES(target_type),
                    target_portal_type = VALUES(target_portal_type),
                    target_content_type = VALUES(target_content_type),
                    target_module_key = VALUES(target_module_key),
                    enabled = 1,
                    updated_at = VALUES(updated_at)
                """,
                (
                    form["name"],
                    form["code"],
                    form["description"],
                    form["targetType"],
                    form["targetPortalType"],
                    form["targetContentType"],
                    form["targetModuleKey"],
                    now,
                    now,
                ),
            )
            row = conn.execute("SELECT id FROM lowcode_forms WHERE code = ?", (form["code"],)).fetchone()
            form_id = row["id"] if row else None
        elif existing:
            form_id = existing["id"]
            conn.execute(
                """
                UPDATE lowcode_forms SET
                    name = ?, description = ?, target_type = ?, target_portal_type = ?,
                    target_content_type = ?, target_module_key = ?, enabled = 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    form["name"],
                    form["description"],
                    form["targetType"],
                    form["targetPortalType"],
                    form["targetContentType"],
                    form["targetModuleKey"],
                    now,
                    form_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO lowcode_forms (
                    name, code, description, target_type, target_portal_type,
                    target_content_type, target_module_key, enabled, created_by,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'system', ?, ?)
                """,
                (
                    form["name"],
                    form["code"],
                    form["description"],
                    form["targetType"],
                    form["targetPortalType"],
                    form["targetContentType"],
                    form["targetModuleKey"],
                    now,
                    now,
                ),
            )
            form_id = cursor.lastrowid
        if not form_id:
            continue
        version = conn.execute(
            "SELECT id FROM lowcode_form_versions WHERE form_id = ? AND version_no = 1",
            (form_id,),
        ).fetchone()
        if version:
            conn.execute(
                """
                UPDATE lowcode_form_versions
                SET schema_json = ?
                WHERE id = ?
                """,
                (json_text(form["schema"], {}), version["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO lowcode_form_versions (
                    form_id, version_no, schema_json, status, created_by, created_at
                )
                VALUES (?, 1, ?, 'active', 'system', ?)
                """,
                (form_id, json_text(form["schema"], {}), now),
            )


def ensure_default_user(conn):
    now = now_iso()
    legacy = conn.execute("SELECT password_hash FROM admin_users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
    password_hash = legacy["password_hash"] if legacy else hash_password(ADMIN_PASSWORD)
    if DATABASE_BACKEND == "mysql":
        conn.execute(
            """
            INSERT INTO users (username, password_hash, display_name, role, department, enabled, created_at, updated_at)
            VALUES (?, ?, ?, 'admin', '', 1, ?, ?)
            ON DUPLICATE KEY UPDATE
                password_hash = CASE WHEN role = 'admin' THEN password_hash ELSE VALUES(password_hash) END,
                display_name = CASE WHEN display_name = '' THEN VALUES(display_name) ELSE display_name END,
                role = 'admin',
                enabled = 1,
                updated_at = VALUES(updated_at)
            """,
            (ADMIN_USERNAME, password_hash, "Administrator", now, now),
        )
        conn.execute("UPDATE projects SET owner_username = ? WHERE owner_username = '' OR owner_username IS NULL", (ADMIN_USERNAME,))
        conn.execute("UPDATE pages SET submitted_by = ? WHERE submitted_by = '' OR submitted_by IS NULL", (ADMIN_USERNAME,))
        conn.execute("UPDATE pages SET reviewed_by = ? WHERE reviewed_by = '' OR reviewed_by IS NULL", (ADMIN_USERNAME,))
        return
    conn.execute(
        """
        INSERT INTO users (username, password_hash, display_name, role, department, enabled, created_at, updated_at)
        VALUES (?, ?, ?, 'admin', '', 1, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            password_hash = CASE WHEN users.role = 'admin' THEN users.password_hash ELSE excluded.password_hash END,
            display_name = CASE WHEN users.display_name = '' THEN excluded.display_name ELSE users.display_name END,
            role = 'admin',
            enabled = 1,
            updated_at = excluded.updated_at
        """,
        (ADMIN_USERNAME, password_hash, "Administrator", now, now),
    )
    conn.execute("UPDATE projects SET owner_username = 'admin' WHERE owner_username = '' OR owner_username IS NULL")
    conn.execute("UPDATE pages SET submitted_by = 'admin' WHERE submitted_by = '' OR submitted_by IS NULL")
    conn.execute("UPDATE pages SET reviewed_by = 'admin' WHERE reviewed_by = '' OR reviewed_by IS NULL")


def page_snapshot_from_row(row):
    return {
        "code": row["code"],
        "category": row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY,
        "source": row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
        "publishedAt": row["published_at"] if "published_at" in row.keys() else "",
        "title": row["title"],
        "subtitle": row["subtitle"],
        "body": row["body"],
        "imageUrl": row["image_url"],
        "contentType": normalize_content_type(row["content_type"] if "content_type" in row.keys() else "article"),
        "accent": row["accent"],
        "enabled": bool(row["enabled"]),
    }


def project_snapshot_from_row(row):
    return {
        "name": row["name"],
        "portalType": normalize_portal_type(row["portal_type"] if "portal_type" in row.keys() else "department"),
        "ownerUsername": row["owner_username"] if "owner_username" in row.keys() else ADMIN_USERNAME,
        "idleKicker": row["idle_kicker"],
        "idleTitle": row["idle_title"],
        "idleCopy": row["idle_copy"],
        "welcomeKicker": row["welcome_kicker"],
        "welcomeTitle": row["welcome_title"],
        "welcomeSubtitle": row["welcome_subtitle"],
        "defaultImageUrl": row["default_image_url"],
        "accent": row["accent"],
        "displayConfig": normalize_display_config(row["display_config"] if "display_config" in row.keys() else "{}"),
    }


def ensure_legacy_versions(conn):
    now = now_iso()
    rows = conn.execute("SELECT * FROM pages").fetchall()
    for row in rows:
        exists = conn.execute(
            "SELECT id FROM page_versions WHERE page_id = ? AND status = 'approved' LIMIT 1",
            (row["id"],),
        ).fetchone()
        if not exists:
            snapshot = page_snapshot_from_row(row)
            conn.execute(
                """
                INSERT INTO page_versions (
                    page_id, project_id, code, operation, status, snapshot,
                    submitted_by, submitted_at, reviewed_by, reviewed_at, changes
                )
                VALUES (?, ?, ?, 'upsert', 'approved', ?, 'admin', ?, 'admin', ?, 'legacy import')
                """,
                (row["id"], row["project_id"], row["code"], json.dumps(snapshot, ensure_ascii=False), now, now),
            )
    project_rows = conn.execute("SELECT * FROM projects").fetchall()
    for row in project_rows:
        exists = conn.execute(
            "SELECT id FROM project_versions WHERE project_id = ? AND status = 'approved' LIMIT 1",
            (row["id"],),
        ).fetchone()
        if not exists:
            snapshot = project_snapshot_from_row(row)
            conn.execute(
                """
                INSERT INTO project_versions (
                    project_id, status, snapshot, submitted_by, submitted_at,
                    reviewed_by, reviewed_at, changes
                )
                VALUES (?, 'approved', ?, 'admin', ?, 'admin', ?, 'legacy import')
                """,
                (row["id"], json.dumps(snapshot, ensure_ascii=False), now, now),
            )
    deployed = conn.execute("SELECT id FROM projects WHERE content_deployed = 1 ORDER BY id LIMIT 1").fetchone()
    if deployed and not conn.execute("SELECT 1 FROM deployed_pages LIMIT 1").fetchone():
        approved_pages = conn.execute(
            "SELECT id FROM pages WHERE project_id = ? AND review_status = 'approved' AND enabled = 1",
            (deployed["id"],),
        ).fetchall()
        for page in approved_pages:
            conn.execute(
                "INSERT OR IGNORE INTO deployed_pages (project_id, page_id, updated_at) VALUES (?, ?, ?)",
                (deployed["id"], page["id"], now),
            )


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password, stored):
    try:
        algo, iterations, salt_hex, hash_hex = str(stored).split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            str(password).encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(derived.hex(), hash_hex)
    except Exception:
        return False


def row_to_user(row):
    if not row:
        return None
    return {
        "username": row["username"],
        "displayName": row["display_name"] or row["username"],
        "role": row["role"],
        "department": row["department"],
        "enabled": bool(row["enabled"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def get_user(username):
    if not username:
        return None
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return row_to_user(row)


def list_users():
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT u.*,
                   COUNT(DISTINCT p.id) AS project_count,
                   COUNT(DISTINCT pages.id) AS page_count
            FROM users u
            LEFT JOIN projects p ON p.owner_username = u.username
            LEFT JOIN pages ON pages.project_id = p.id
            GROUP BY u.username
            ORDER BY CASE u.role WHEN 'admin' THEN 0 ELSE 1 END, u.enabled DESC, u.username
            """
        ).fetchall()
    users = []
    for row in rows:
        user = row_to_user(row)
        user["projectCount"] = int(row["project_count"] or 0)
        user["pageCount"] = int(row["page_count"] or 0)
        users.append(user)
    return users


def upsert_user(data, actor="admin"):
    username = str(data.get("username", "")).strip()
    if not username:
        raise ValueError("username 不能为空")
    if not re.match(r"^[A-Za-z0-9_.-]{2,64}$", username):
        raise ValueError("username 只能使用字母、数字、点、短横线或下划线")
    role = str(data.get("role") or "teacher").strip()
    if role not in {"admin", "teacher"}:
        role = "teacher"
    display_name = str(data.get("displayName") or data.get("name") or username).strip()
    department = str(data.get("department") or "").strip()
    enabled = 1 if data.get("enabled", True) else 0
    password = str(data.get("password") or "").strip()
    now = now_iso()
    with db_connect() as conn:
        current = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
        if current:
            password = validate_user_password(password, username, display_name, required=False)
            fields = [display_name, role, department, enabled, now, username]
            conn.execute(
                """
                UPDATE users SET display_name = ?, role = ?, department = ?,
                    enabled = ?, updated_at = ?
                WHERE username = ?
                """,
                fields,
            )
            if password:
                conn.execute(
                    "UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?",
                    (hash_password(password), now, username),
                )
        else:
            password = validate_user_password(password, username, display_name, required=True)
            conn.execute(
                """
                INSERT INTO users (
                    username, password_hash, display_name, role, department, enabled, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (username, hash_password(password), display_name, role, department, enabled, now, now),
            )
    return get_user(username)


def reset_user_password(username, password):
    password = validate_user_password(password, username, required=True)
    with db_connect() as conn:
        row = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?",
            (hash_password(password), now_iso(), username),
        )
    return get_user(username)


def set_user_enabled(username, enabled):
    if username == ADMIN_USERNAME and not enabled:
        raise ValueError("admin 账号不能被禁用")
    with db_connect() as conn:
        row = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE users SET enabled = ?, updated_at = ? WHERE username = ?",
            (1 if enabled else 0, now_iso(), username),
        )
    return get_user(username)


def change_password(username, old_password, new_password):
    new_password = validate_user_password(new_password, username, required=True)
    with db_connect() as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if not row or not verify_password(old_password, row["password_hash"]):
            raise ValueError("当前 password 不正确")
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?",
            (hash_password(new_password), now_iso(), username),
        )


def create_admin_session(username):
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + ADMIN_SESSION_SECONDS
    with db_connect() as conn:
        conn.execute(
            "INSERT INTO user_sessions (token, username, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (token, username, expires_at, now_iso()),
        )
        conn.execute("DELETE FROM user_sessions WHERE expires_at <= ?", (int(time.time()),))
    return token


def get_session_user(token):
    if not token:
        return None
    now = int(time.time())
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT sessions.username, sessions.expires_at, users.*
            FROM user_sessions sessions
            JOIN users ON users.username = sessions.username
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()
        if not row:
            return None
        if int(row["expires_at"]) <= now:
            conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
            return None
        if not bool(row["enabled"]):
            conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
            return None
        return row_to_user(row)


def get_session_username(token):
    user = get_session_user(token)
    return user["username"] if user else None


def delete_admin_session(token):
    if not token:
        return
    with db_connect() as conn:
        conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))


def default_display_config():
    return json.loads(json.dumps(DEFAULT_DISPLAY_CONFIG, ensure_ascii=False))


def clean_config_text(value):
    return str(value or "").strip()


def normalize_text_list(value, fallback, max_items=8):
    if isinstance(value, list):
        items = [clean_config_text(item) for item in value]
    else:
        text = clean_config_text(value)
        items = re.split(r"[\n,，、]+", text) if text else []
    items = [item for item in items if item]
    return items[:max_items] if items else []


def normalize_display_config(value):
    if isinstance(value, str):
        try:
            value = json.loads(value or "{}")
        except json.JSONDecodeError:
            value = {}
    if not isinstance(value, dict):
        value = {}

    config = default_display_config()
    text_fields = (
        "logoImageUrl",
        "schoolName",
        "schoolMeta",
        "badgeText",
        "summaryLabel",
        "summaryTitle",
        "summaryCopy",
        "scanTitle",
        "scanCopy",
        "scanImageUrl",
        "sideTitle",
        "sideCopy",
        "brandColor",
        "brandDeepColor",
        "accent2",
    )
    for field in text_fields:
        if field in value:
            config[field] = clean_config_text(value.get(field))

    if "summaryTags" in value:
        config["summaryTags"] = normalize_text_list(
            value.get("summaryTags"),
            DEFAULT_DISPLAY_CONFIG["summaryTags"],
        )

    source_slides = value.get("slides")
    if not isinstance(source_slides, list):
        source_slides = []

    slides = []
    default_slides = DEFAULT_DISPLAY_CONFIG["slides"]
    slide_count = max(len(default_slides), min(len(source_slides), 6))
    for index in range(slide_count):
        fallback = dict(default_slides[index]) if index < len(default_slides) else {
            "label": f"轮播内容 {index + 1}",
            "meta": f"欢迎 {index + 1:02d}",
            "title": "校园内容",
            "body": "",
            "imageUrl": "",
            "visual": "gate",
        }
        source = source_slides[index] if index < len(source_slides) and isinstance(source_slides[index], dict) else {}
        slide = {}
        for field in ("label", "meta", "title", "body", "imageUrl", "visual"):
            slide[field] = clean_config_text(source.get(field, fallback.get(field, "")))
        slides.append(slide)
    config["slides"] = slides
    return config


def display_config_json(value):
    return json.dumps(normalize_display_config(value), ensure_ascii=False, separators=(",", ":"))


def row_to_project(row):
    if not row:
        return None
    display_config = row["display_config"] if "display_config" in row.keys() else "{}"
    content_deployed = row["content_deployed"] if "content_deployed" in row.keys() else row["deployed"]
    page_count = row["page_count"] if "page_count" in row.keys() else 0
    scan_count = row["scan_count"] if "scan_count" in row.keys() else 0
    pending_page_count = row["pending_page_count"] if "pending_page_count" in row.keys() else 0
    owner_username = row["owner_username"] if "owner_username" in row.keys() else ADMIN_USERNAME
    owner_display_name = row["owner_display_name"] if "owner_display_name" in row.keys() else owner_username
    owner_enabled = row["owner_enabled"] if "owner_enabled" in row.keys() else 1
    portal_type = normalize_portal_type(row["portal_type"] if "portal_type" in row.keys() else "department")
    portal_slug = normalize_portal_slug(row["portal_slug"] if "portal_slug" in row.keys() else "")
    return {
        "id": row["id"],
        "name": row["name"],
        "portalType": portal_type,
        "portalTypeLabel": portal_type_label(portal_type),
        "portalSlug": portal_slug,
        "previewUrl": portal_preview_url(portal_type, portal_slug),
        "ownerUsername": owner_username,
        "ownerDisplayName": owner_display_name or owner_username,
        "ownerEnabled": bool(owner_enabled),
        "idleKicker": row["idle_kicker"],
        "idleTitle": row["idle_title"],
        "idleCopy": row["idle_copy"],
        "welcomeKicker": row["welcome_kicker"],
        "welcomeTitle": row["welcome_title"],
        "welcomeSubtitle": row["welcome_subtitle"],
        "defaultImageUrl": row["default_image_url"],
        "accent": row["accent"],
        "displayConfig": normalize_display_config(display_config),
        "deployed": bool(row["deployed"]),
        "contentDeployed": bool(content_deployed),
        "configStatus": row["config_status"] if "config_status" in row.keys() else "approved",
        "pendingConfigVersionId": row["pending_config_version_id"] if "pending_config_version_id" in row.keys() else None,
        "pageCount": int(page_count or 0),
        "pendingPageCount": int(pending_page_count or 0),
        "scanCount": int(scan_count or 0),
        "updatedAt": row["updated_at"],
    }


def get_project(project_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.id = ?
            """,
            (project_id,),
        ).fetchone()
    return row_to_project(row)


def project_accessible(project, user):
    if not project or not user:
        return False
    if user.get("role") == "admin":
        return True
    return project.get("ownerUsername") == user.get("username")


def get_deployed_project():
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.deployed = 1 AND COALESCE(users.enabled, 1) = 1
            ORDER BY p.id LIMIT 1
            """
        ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
                FROM projects p
                LEFT JOIN users ON users.username = p.owner_username
                WHERE COALESCE(users.enabled, 1) = 1
                ORDER BY p.id LIMIT 1
                """
            ).fetchone()
    return row_to_project(row)


def get_deployed_content_project():
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.content_deployed = 1 AND COALESCE(users.enabled, 1) = 1
            ORDER BY p.id LIMIT 1
            """
        ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
                FROM projects p
                LEFT JOIN users ON users.username = p.owner_username
                WHERE p.deployed = 1 AND COALESCE(users.enabled, 1) = 1
                ORDER BY p.id LIMIT 1
                """
            ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
                FROM projects p
                LEFT JOIN users ON users.username = p.owner_username
                WHERE COALESCE(users.enabled, 1) = 1
                ORDER BY p.id LIMIT 1
                """
            ).fetchone()
    return row_to_project(row)


def list_projects(user=None):
    user = user or {"role": "admin"}
    owner_filter = ""
    params = []
    if user.get("role") != "admin":
        owner_filter = "WHERE p.owner_username = ?"
        params.append(user.get("username", ""))
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT
                p.*,
                users.display_name AS owner_display_name,
                users.enabled AS owner_enabled,
                COUNT(DISTINCT pages.id) AS page_count,
                SUM(CASE WHEN pages.review_status IN ('pending','pending_delete','rejected') THEN 1 ELSE 0 END) AS pending_page_count,
                COUNT(DISTINCT scans.id) AS scan_count
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            LEFT JOIN pages ON pages.project_id = p.id
            LEFT JOIN scans ON scans.project_id = p.id
            {owner_filter}
            GROUP BY p.id
            ORDER BY p.deployed DESC, p.content_deployed DESC, p.updated_at DESC, p.id DESC
            """,
            params,
        ).fetchall()
    return [row_to_project(row) for row in rows]


def module_key_for_category(category, portal_type="department"):
    text = str(category or "").strip().lower()
    if not text:
        return ""
    modules = module_set_for_portal_type(portal_type)
    for module in modules:
        if text == module["label"].lower() or text == module["key"].lower():
            return module["key"]
    for module in modules:
        for alias in module["aliases"]:
            if alias and alias.lower() in text:
                return module["key"]
    return ""


def standard_module_payload(module, pages=None):
    pages = pages or []
    approved = [
        page for page in pages
        if page.get("enabled", True) and page.get("reviewStatus", "approved") == "approved"
    ]
    pending = [
        page for page in pages
        if page.get("reviewStatus") in {"pending", "pending_delete"}
    ]
    return {
        "key": module["key"],
        "label": module["label"],
        "description": module["description"],
        "count": len(pages),
        "approvedCount": len(approved),
        "pendingCount": len(pending),
        "covered": bool(pages),
        "publishReady": bool(approved),
        "pages": [
            {
                "id": page.get("id"),
                "code": page.get("code", ""),
                "title": page.get("title", ""),
                "reviewStatus": page.get("reviewStatus", ""),
                "enabled": bool(page.get("enabled", True)),
            }
            for page in pages[:6]
        ],
    }


def module_coverage_from_pages(pages, portal_type="department"):
    normalized_portal_type = normalize_portal_type(portal_type)
    modules_config = module_set_for_portal_type(normalized_portal_type)
    grouped = {module["key"]: [] for module in modules_config}
    unmatched = []
    for page in pages or []:
        module_key = page.get("moduleKey") or module_key_for_category(page.get("category", ""), normalized_portal_type)
        if module_key in grouped:
            grouped[module_key].append(page)
        else:
            unmatched.append(page)
    modules = [standard_module_payload(module, grouped[module["key"]]) for module in modules_config]
    covered = sum(1 for module in modules if module["covered"])
    publish_ready = sum(1 for module in modules if module["publishReady"])
    return {
        "portalType": normalized_portal_type,
        "portalTypeLabel": portal_type_label(normalized_portal_type),
        "total": len(modules),
        "covered": covered,
        "missing": len(modules) - covered,
        "publishReady": publish_ready,
        "modules": modules,
        "missingLabels": [module["label"] for module in modules if not module["covered"]],
        "unmatched": [
            {
                "id": page.get("id"),
                "code": page.get("code", ""),
                "title": page.get("title", ""),
                "category": page.get("category", ""),
            }
            for page in unmatched[:8]
        ],
    }


def create_admin_log(action, target_type="", target_id="", target_label="", detail="", username="", role="", ip="", changes=""):
    try:
        with db_connect() as conn:
            conn.execute(
                """
                INSERT INTO admin_logs (
                    username, role, action, target_type, target_id, target_label, detail, changes, ip, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(username or ""),
                    str(role or ""),
                    str(action or ""),
                    str(target_type or ""),
                    str(target_id or ""),
                    str(target_label or ""),
                    str(detail or ""),
                    str(changes or ""),
                    str(ip or ""),
                    now_iso(),
                ),
            )
    except DBError as exc:
        print(f"admin log failed: {exc}")


def row_to_admin_log(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"] if "role" in row.keys() else "",
        "action": row["action"],
        "targetType": row["target_type"],
        "targetId": row["target_id"],
        "targetLabel": row["target_label"],
        "detail": row["detail"],
        "changes": row["changes"] if "changes" in row.keys() else "",
        "ip": row["ip"],
        "createdAt": row["created_at"],
    }


def list_admin_logs(limit=80, username="", action="", date_from="", date_to=""):
    limit = max(1, min(int(limit or 80), 300))
    where = []
    params = []
    if username:
        where.append("username = ?")
        params.append(username)
    if action:
        where.append("action = ?")
        params.append(action)
    if date_from:
        where.append("created_at >= ?")
        params.append(date_from)
    if date_to:
        where.append("created_at <= ?")
        params.append(date_to)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM admin_logs
            {where_sql}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()
    return [row_to_admin_log(row) for row in rows]


def operations_summary(user=None):
    user = user or {"role": "admin", "username": ""}
    ready = ready_status()
    owner_join = ""
    owner_where = ""
    owner_params = []
    if user.get("role") != "admin":
        owner_join = "JOIN projects ON projects.id = pages.project_id"
        owner_where = "WHERE projects.owner_username = ?"
        owner_params.append(user.get("username", ""))
    with db_connect() as conn:
        deployed = conn.execute(
            """
            SELECT
                MAX(CASE WHEN deployed = 1 THEN id ELSE 0 END) AS welcome_id,
                MAX(CASE WHEN deployed = 1 THEN name ELSE '' END) AS welcome_name,
                MAX(CASE WHEN content_deployed = 1 THEN id ELSE 0 END) AS content_id,
                MAX(CASE WHEN content_deployed = 1 THEN name ELSE '' END) AS content_name
            FROM projects
            """
        ).fetchone()
        pending_pages = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages
            {owner_join}
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.review_status IN ('pending','pending_delete')
            """,
            owner_params,
        ).fetchone()["value"]
        pending_projects = 0
        if user.get("role") == "admin":
            pending_projects = conn.execute(
                "SELECT COUNT(*) AS value FROM projects WHERE config_status = 'pending'"
            ).fetchone()["value"]
        asset_count = conn.execute(
            "SELECT COUNT(*) AS value FROM assets" if user.get("role") == "admin" else "SELECT COUNT(*) AS value FROM assets WHERE owner_username = ?",
            () if user.get("role") == "admin" else (user.get("username", ""),),
        ).fetchone()["value"]
        recent_errors = conn.execute(
            """
            SELECT * FROM admin_logs
            WHERE action IN ('deploy_content','review_reject','disable_user')
            ORDER BY created_at DESC, id DESC
            LIMIT 5
            """
        ).fetchall() if user.get("role") == "admin" else []
    return {
        "ready": ready,
        "deployed": {
            "welcomeProjectId": int(deployed["welcome_id"] or 0),
            "welcomeProjectName": deployed["welcome_name"] or "",
            "contentProjectId": int(deployed["content_id"] or 0),
            "contentProjectName": deployed["content_name"] or "",
        },
        "pending": {
            "pages": int(pending_pages or 0),
            "projects": int(pending_projects or 0),
        },
        "assets": {"count": int(asset_count or 0)},
        "recentErrors": [row_to_admin_log(row) for row in recent_errors],
        "config": online_config_audit() if user.get("role") == "admin" else {"ok": True, "errors": [], "warnings": []},
    }


def config_issue(level, code, message):
    return {"level": level, "code": code, "message": message}


def online_config_audit():
    errors = []
    warnings = []
    is_online = online_mode_enabled()
    public_base = PUBLIC_BASE_URL.strip()
    if not is_online:
        warnings.append(config_issue("warning", "local_mode", "当前仍是本地模式；公网部署前需要配置 PUBLIC_BASE_URL、MySQL 或对象存储。"))
    if not public_base:
        warnings.append(config_issue("warning", "public_base_url", "未配置 PUBLIC_BASE_URL，线上二维码、Cookie 和反代判断缺少公网基准地址。"))
    elif not public_base.startswith("https://"):
        warnings.append(config_issue("warning", "public_base_url_https", "PUBLIC_BASE_URL 不是 HTTPS；正式公网建议使用 HTTPS。"))
    if public_base.startswith("https://") and not SESSION_COOKIE_SECURE:
        errors.append(config_issue("error", "secure_cookie", "HTTPS 公网地址下 SESSION_COOKIE_SECURE 必须开启。"))
    if is_online and ADMIN_PASSWORD in WEAK_ONLINE_SECRETS:
        errors.append(config_issue("error", "admin_password", "线上模式不能使用默认或占位管理员密码。"))
    if is_online and CSRF_SECRET in WEAK_ONLINE_SECRETS:
        errors.append(config_issue("error", "csrf_secret", "线上模式必须配置强随机 CSRF_SECRET。"))
    if PASSWORD_MIN_LENGTH < 10:
        errors.append(config_issue("error", "password_min_length", "PASSWORD_MIN_LENGTH 不应低于 10。"))
    if ALLOW_WEAK_USER_PASSWORDS:
        errors.append(config_issue("error", "weak_user_passwords", "ALLOW_WEAK_USER_PASSWORDS 已开启，线上必须关闭。"))
    if DATABASE_BACKEND != "mysql":
        warnings.append(config_issue("warning", "database_backend", "当前数据库不是 MySQL；多人线上正式环境建议使用 MySQL。"))
    if asset_storage_backend() == "local":
        warnings.append(config_issue("warning", "asset_storage", "当前资源存储为本地 uploads；多实例或云部署建议使用对象存储。"))
    if ALLOW_SVG_UPLOADS:
        warnings.append(config_issue("warning", "svg_uploads", "SVG 上传已开启；线上建议关闭，避免脚本型 SVG 风险。"))
    if LOGIN_RATE_LIMIT <= 0:
        warnings.append(config_issue("warning", "login_rate_limit", "登录限流已关闭。"))
    if UPLOAD_RATE_LIMIT <= 0:
        warnings.append(config_issue("warning", "upload_rate_limit", "上传限流已关闭。"))
    if is_online and not TRUST_PROXY_HEADERS:
        warnings.append(config_issue("warning", "proxy_headers", "线上反代部署通常需要 TRUST_PROXY_HEADERS=1 以记录真实客户端 IP。"))
    return {
        "ok": not errors,
        "onlineMode": is_online,
        "errors": errors,
        "warnings": warnings,
    }


def acceptance_report(user):
    dashboard = admin_dashboard(user)
    operations = dashboard.get("operations", {})
    deployed = operations.get("deployed", {})
    content_project_id = int(deployed.get("contentProjectId") or 0)
    content_check = deploy_content_check(content_project_id) if content_project_id else {
        "ok": False,
        "projectId": 0,
        "pageIds": [],
        "errors": ["内容项目尚未部署"],
        "warnings": [],
        "eligiblePageIds": [],
    }
    reviews = list_reviews("pending")
    return {
        "ok": bool(operations.get("ready", {}).get("ok")) and bool(operations.get("config", {}).get("ok")) and bool(content_check.get("ok")),
        "generatedAt": now_iso(),
        "generatedBy": user.get("username", ""),
        "summary": dashboard.get("summary", {}),
        "ready": operations.get("ready", {}),
        "config": operations.get("config", {}),
        "deployed": deployed,
        "deployCheck": content_check,
        "pending": {
            "pages": len(reviews.get("pages", [])),
            "projects": len(reviews.get("projects", [])),
            "contentItems": len(reviews.get("contentItems", [])),
        },
        "assets": operations.get("assets", {}),
        "recentErrors": operations.get("recentErrors", []),
    }


def row_to_asset(row):
    if not row:
        return None
    return {
        "id": row["id"],
        "ownerUsername": row["owner_username"],
        "originalFilename": row["original_filename"],
        "storageKey": row["storage_key"],
        "url": row["url"],
        "mimeType": row["mime_type"],
        "sizeBytes": int(row["size_bytes"] or 0),
        "backend": row["backend"],
        "createdAt": row["created_at"],
    }


def list_assets(user, limit=80):
    try:
        limit = int(limit or 80)
    except (TypeError, ValueError):
        limit = 80
    limit = max(1, min(limit, 200))
    where = ""
    params = []
    if user.get("role") != "admin":
        where = "WHERE owner_username = ?"
        params.append(user.get("username", ""))
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT *
            FROM assets
            {where}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()
    return [row_to_asset(row) for row in rows]


def get_asset(asset_id):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    return row_to_asset(row)


def asset_accessible(asset, user):
    if not asset or not user:
        return False
    if user.get("role") == "admin":
        return True
    return asset.get("ownerUsername") == user.get("username")


def create_asset_record(user, original_filename, storage_key, url, mime_type, size_bytes):
    with db_connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO assets (
                owner_username, original_filename, storage_key, url,
                mime_type, size_bytes, backend, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.get("username", ""),
                str(original_filename or "")[:255],
                storage_key,
                url,
                mime_type,
                int(size_bytes or 0),
                asset_storage_backend(),
                now_iso(),
            ),
        )
        asset_id = cursor.lastrowid
    return get_asset(asset_id)


def asset_usage_summary(url):
    empty = {"projects": 0, "pages": 0, "contentItems": 0, "pendingPageVersions": 0, "pendingProjectVersions": 0, "total": 0}
    if not url:
        return empty
    pattern = f"%{url}%"
    with db_connect() as conn:
        projects = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM projects
            WHERE default_image_url = ? OR display_config LIKE ?
            """,
            (url, pattern),
        ).fetchone()["value"]
        pages = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM pages
            WHERE image_url = ? OR body LIKE ?
            """,
            (url, pattern),
        ).fetchone()["value"]
        content_items = conn.execute(
            """
            SELECT COUNT(DISTINCT content_items.id) AS value
            FROM content_items
            LEFT JOIN assets cover ON cover.id = content_items.cover_asset_id
            LEFT JOIN content_item_assets cia ON cia.content_item_id = content_items.id
            LEFT JOIN assets linked ON linked.id = cia.asset_id
            WHERE cover.url = ? OR linked.url = ? OR cia.url = ?
               OR content_items.body_json LIKE ? OR content_items.meta_json LIKE ?
            """,
            (url, url, url, pattern, pattern),
        ).fetchone()["value"] if table_exists(conn, "content_items") else 0
        page_versions = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM page_versions
            WHERE status = 'pending' AND snapshot LIKE ?
            """,
            (pattern,),
        ).fetchone()["value"]
        project_versions = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM project_versions
            WHERE status = 'pending' AND snapshot LIKE ?
            """,
            (pattern,),
        ).fetchone()["value"]
    summary = {
        "projects": int(projects or 0),
        "pages": int(pages or 0),
        "contentItems": int(content_items or 0),
        "pendingPageVersions": int(page_versions or 0),
        "pendingProjectVersions": int(project_versions or 0),
    }
    summary["total"] = sum(summary.values())
    return summary


def asset_usage_message(summary):
    parts = []
    if summary.get("projects"):
        parts.append(f"{summary['projects']} 个项目")
    if summary.get("pages"):
        parts.append(f"{summary['pages']} 个展示页")
    if summary.get("contentItems"):
        parts.append(f"{summary['contentItems']} 条结构化资料")
    if summary.get("pendingPageVersions"):
        parts.append(f"{summary['pendingPageVersions']} 个待审核页面草稿")
    if summary.get("pendingProjectVersions"):
        parts.append(f"{summary['pendingProjectVersions']} 个待审核项目草稿")
    return "资源正在被使用：" + "，".join(parts) if parts else "资源正在被使用"


def delete_asset(asset_id, user):
    asset = get_asset(asset_id)
    if not asset or not asset_accessible(asset, user):
        return None
    usage = asset_usage_summary(asset["url"])
    if usage["total"]:
        raise ValueError(asset_usage_message(usage))
    asset_storage(UPLOAD_DIR).delete(asset["storageKey"])
    with db_connect() as conn:
        conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    return asset


def json_value(value, fallback):
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return fallback
    text = str(value or "").strip()
    if not text:
        return fallback
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return fallback


def json_text(value, fallback):
    return json.dumps(value if value is not None else fallback, ensure_ascii=False)


def int_value(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def bool_value(value, default=False):
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "是"}
    return bool(value)


def content_body_json_from_data(value, legacy_body=""):
    if isinstance(value, (dict, list)):
        return value
    text = str(value or legacy_body or "").strip()
    if not text:
        return []
    if re.search(r"<[a-z][\s\S]*>", text, flags=re.I):
        return [{"type": "html", "html": sanitize_rich_html(text)}]
    return [
        {"type": "paragraph", "text": item.strip()}
        for item in re.split(r"\n{2,}", text)
        if item.strip()
    ]


def content_assets_from_data(value):
    if not isinstance(value, list):
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            continue
        asset_id = int_value(item.get("assetId") or item.get("asset_id"))
        result.append(
            {
                "id": int_value(item.get("id")),
                "assetId": asset_id if asset_id > 0 else None,
                "role": str(item.get("role") or "gallery").strip()[:40] or "gallery",
                "title": str(item.get("title") or "").strip()[:255],
                "caption": str(item.get("caption") or "").strip()[:512],
                "url": str(item.get("url") or "").strip()[:2048],
                "sortOrder": int_value(item.get("sortOrder") if "sortOrder" in item else item.get("sort_order"), index),
            }
        )
    return result


def validate_content_asset_access(cover_asset_id, assets, user):
    asset_ids = {int_value(cover_asset_id)}
    asset_ids.update(int_value(item.get("assetId")) for item in assets or [])
    for asset_id in sorted(item for item in asset_ids if item > 0):
        asset = get_asset(asset_id)
        if not asset or not asset_accessible(asset, user):
            raise ValueError(f"素材 {asset_id} 不存在或无权使用")


def content_item_asset_rows(conn, content_item_id):
    rows = conn.execute(
        """
        SELECT
            content_item_assets.*,
            assets.url AS asset_url,
            assets.original_filename AS asset_filename
        FROM content_item_assets
        LEFT JOIN assets ON assets.id = content_item_assets.asset_id
        WHERE content_item_assets.content_item_id = ?
        ORDER BY content_item_assets.sort_order, content_item_assets.id
        """,
        (content_item_id,),
    ).fetchall()
    result = []
    for row in rows:
        result.append(
            {
                "id": row["id"],
                "assetId": row["asset_id"],
                "role": row["role"],
                "title": row["title"],
                "caption": row["caption"],
                "url": row["url"] or row["asset_url"] or "",
                "assetFilename": row["asset_filename"] or "",
                "sortOrder": int(row["sort_order"] or 0),
                "createdAt": row["created_at"],
            }
        )
    return result


def row_to_content_item(row, assets=None, project=None):
    if not row:
        return None
    portal_type = normalize_portal_type(
        (project or {}).get("portalType")
        or (row["project_portal_type"] if "project_portal_type" in row.keys() else "department")
    )
    module_key = str(row["module_key"] or "").strip()
    module_meta = module_meta_for_key(module_key, portal_type)
    content_type = normalize_content_type(row["content_type"])
    return {
        "id": row["id"],
        "projectId": row["project_id"],
        "pageId": row["page_id"] if "page_id" in row.keys() else None,
        "code": row["code"],
        "moduleKey": module_key,
        "moduleLabel": module_meta["label"] if module_meta else module_key,
        "contentType": content_type,
        "contentTypeLabel": content_type_label(content_type),
        "title": row["title"],
        "subtitle": row["subtitle"],
        "summary": row["summary"],
        "bodyJson": json_value(row["body_json"], []),
        "metaJson": json_value(row["meta_json"], {}),
        "coverAssetId": row["cover_asset_id"],
        "sortOrder": int(row["sort_order"] or 0),
        "featured": bool(row["featured"]),
        "enabled": bool(row["enabled"]),
        "reviewStatus": row["review_status"],
        "pendingVersionId": row["pending_version_id"],
        "submittedBy": row["submitted_by"],
        "reviewedBy": row["reviewed_by"],
        "reviewNote": row["review_note"],
        "assets": assets or [],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def get_content_item(project_id, content_item_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT content_items.*, projects.portal_type AS project_portal_type
            FROM content_items
            JOIN projects ON projects.id = content_items.project_id
            WHERE content_items.project_id = ? AND content_items.id = ?
            """,
            (project_id, content_item_id),
        ).fetchone()
        assets = content_item_asset_rows(conn, content_item_id) if row else []
    return row_to_content_item(row, assets)


def get_content_item_by_id(content_item_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT content_items.*, projects.portal_type AS project_portal_type
            FROM content_items
            JOIN projects ON projects.id = content_items.project_id
            WHERE content_items.id = ?
            """,
            (content_item_id,),
        ).fetchone()
        assets = content_item_asset_rows(conn, content_item_id) if row else []
    return row_to_content_item(row, assets)


def list_content_items(project_id, filters=None):
    filters = filters or {}
    where = ["content_items.project_id = ?"]
    params = [project_id]
    if filters.get("moduleKey"):
        where.append("content_items.module_key = ?")
        params.append(str(filters["moduleKey"]))
    if filters.get("contentType"):
        where.append("content_items.content_type = ?")
        params.append(normalize_content_type(filters["contentType"]))
    if filters.get("reviewStatus"):
        where.append("content_items.review_status = ?")
        params.append(str(filters["reviewStatus"]))
    if filters.get("enabled") in {"0", "1", 0, 1, False, True}:
        where.append("content_items.enabled = ?")
        params.append(1 if bool_value(filters.get("enabled")) else 0)
    sql = " AND ".join(where)
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT content_items.*, projects.portal_type AS project_portal_type
            FROM content_items
            JOIN projects ON projects.id = content_items.project_id
            WHERE {sql}
            ORDER BY content_items.module_key, content_items.sort_order, content_items.updated_at DESC, content_items.id DESC
            """,
            params,
        ).fetchall()
        asset_map = {row["id"]: content_item_asset_rows(conn, row["id"]) for row in rows}
    return [row_to_content_item(row, asset_map.get(row["id"], [])) for row in rows]


def row_to_lowcode_form(row, version_row=None):
    if not row:
        return None
    schema = json_value(version_row["schema_json"], {}) if version_row else {}
    return {
        "id": row["id"],
        "name": row["name"],
        "code": row["code"],
        "description": row["description"],
        "targetType": row["target_type"],
        "targetPortalType": normalize_portal_type(row["target_portal_type"]),
        "targetContentType": normalize_content_type(row["target_content_type"]),
        "targetModuleKey": row["target_module_key"],
        "enabled": bool(row["enabled"]),
        "createdBy": row["created_by"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
        "version": {
            "id": version_row["id"],
            "versionNo": int(version_row["version_no"] or 1),
            "status": version_row["status"],
            "createdBy": version_row["created_by"],
            "createdAt": version_row["created_at"],
        } if version_row else None,
        "schema": schema,
    }


def active_lowcode_form_version(conn, form_id):
    return conn.execute(
        """
        SELECT * FROM lowcode_form_versions
        WHERE form_id = ? AND status = 'active'
        ORDER BY version_no DESC, id DESC
        LIMIT 1
        """,
        (form_id,),
    ).fetchone()


def list_lowcode_forms(filters=None):
    filters = filters or {}
    where = []
    params = []
    if filters.get("portalType"):
        where.append("target_portal_type = ?")
        params.append(normalize_portal_type(filters["portalType"]))
    if filters.get("moduleKey"):
        where.append("target_module_key = ?")
        params.append(str(filters["moduleKey"]))
    if filters.get("enabled") in {"0", "1", 0, 1, False, True}:
        where.append("enabled = ?")
        params.append(1 if bool_value(filters.get("enabled")) else 0)
    sql = f"WHERE {' AND '.join(where)}" if where else ""
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM lowcode_forms
            {sql}
            ORDER BY target_portal_type, id
            """,
            params,
        ).fetchall()
        versions = {row["id"]: active_lowcode_form_version(conn, row["id"]) for row in rows}
    return [row_to_lowcode_form(row, versions.get(row["id"])) for row in rows]


def get_lowcode_form(form_id):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM lowcode_forms WHERE id = ?", (form_id,)).fetchone()
        version = active_lowcode_form_version(conn, form_id) if row else None
    return row_to_lowcode_form(row, version)


def latest_lowcode_version_no(conn, form_id):
    row = conn.execute(
        "SELECT MAX(version_no) AS value FROM lowcode_form_versions WHERE form_id = ?",
        (form_id,),
    ).fetchone()
    return int(row["value"] or 0) if row else 0


def row_to_lowcode_form_version(row):
    if not row:
        return None
    schema = json_value(row["schema_json"], {})
    fields = schema.get("fields") if isinstance(schema, dict) and isinstance(schema.get("fields"), list) else []
    return {
        "id": row["id"],
        "formId": row["form_id"],
        "versionNo": int(row["version_no"] or 0),
        "status": row["status"],
        "fieldCount": len([field for field in fields if isinstance(field, dict) and field.get("type") != "asset_list"]),
        "schema": schema,
        "createdBy": row["created_by"],
        "createdAt": row["created_at"],
    }


def list_lowcode_form_versions(form_id):
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM lowcode_form_versions
            WHERE form_id = ?
            ORDER BY version_no DESC, id DESC
            """,
            (form_id,),
        ).fetchall()
    return [row_to_lowcode_form_version(row) for row in rows]


def unique_lowcode_form_code(conn, base_code):
    base = re.sub(r"[^A-Za-z0-9_-]+", "-", str(base_code or "LC-COPY").strip()).strip("-").upper()[:100] or "LC-COPY"
    code = base
    index = 2
    while conn.execute("SELECT id FROM lowcode_forms WHERE code = ? LIMIT 1", (code,)).fetchone():
        code = f"{base}-{index}"
        index += 1
    return code


def copy_lowcode_form(form_id, data, actor):
    source = get_lowcode_form(form_id)
    if not source:
        raise ValueError("模板不存在")
    with db_connect() as conn:
        code = unique_lowcode_form_code(conn, data.get("code") or f"{source['code']}-COPY")
    name = str(data.get("name") or f"{source['name']} 副本").strip()
    payload = {
        "name": name,
        "code": code,
        "description": str(data.get("description") or source.get("description") or "").strip(),
        "targetPortalType": source.get("targetPortalType"),
        "targetModuleKey": source.get("targetModuleKey"),
        "targetContentType": source.get("targetContentType"),
        "enabled": bool_value(data.get("enabled"), False),
        "schema": source.get("schema") or {},
    }
    return save_lowcode_form(None, payload, actor)


def normalize_lowcode_schema(schema, form):
    schema = json_value(schema, {})
    if not isinstance(schema, dict):
        schema = {}
    fields = schema.get("fields") if isinstance(schema.get("fields"), list) else []
    normalized_fields = []
    for index, field in enumerate(fields):
        if not isinstance(field, dict):
            continue
        key = str(field.get("key") or "").strip()
        label = str(field.get("label") or key).strip()
        if not key or not label:
            continue
        normalized = {
            "key": key[:80],
            "label": label[:120],
            "type": str(field.get("type") or "text").strip()[:40] or "text",
            "required": bool_value(field.get("required")),
            "mapping": str(field.get("mapping") or "").strip()[:160],
            "placeholder": str(field.get("placeholder") or "").strip()[:512],
            "defaultValue": str(field.get("defaultValue") if "defaultValue" in field else field.get("default_value") or "").strip()[:1024],
            "sortOrder": int_value(field.get("sortOrder"), index),
        }
        options = field.get("options")
        if isinstance(options, list):
            normalized["options"] = [
                {
                    "label": str(item.get("label") if isinstance(item, dict) else item).strip(),
                    "value": str(item.get("value") if isinstance(item, dict) else item).strip(),
                }
                for item in options
                if str(item.get("value") if isinstance(item, dict) else item).strip()
            ]
        normalized_fields.append(normalized)
    if not normalized_fields:
        module = module_meta_for_key(form.get("targetModuleKey"), form.get("targetPortalType")) or {
            "key": form.get("targetModuleKey") or "overview",
            "label": form.get("name") or "资料",
            "description": form.get("description") or "",
        }
        schema = lowcode_schema_for_module(form.get("targetPortalType", "department"), module)
    else:
        schema["fields"] = sorted(normalized_fields, key=lambda item: item.get("sortOrder", 0))
    schema["moduleKey"] = form.get("targetModuleKey") or schema.get("moduleKey") or ""
    schema["contentType"] = normalize_content_type(form.get("targetContentType") or schema.get("contentType"))
    schema["portalType"] = normalize_portal_type(form.get("targetPortalType") or schema.get("portalType"))
    schema["moduleLabel"] = schema.get("moduleLabel") or (module_meta_for_key(schema["moduleKey"], schema["portalType"]) or {}).get("label", schema["moduleKey"])
    schema["contentTypeLabel"] = content_type_label(schema["contentType"])
    schema["mapping"] = {
        "target": "content_items",
        "moduleKey": schema["moduleKey"],
        "contentType": schema["contentType"],
    }
    return schema


def save_lowcode_form(form_id, data, actor):
    name = str(data.get("name") or "").strip()[:255]
    if not name:
        raise ValueError("模板名称不能为空")
    code = re.sub(r"[^A-Za-z0-9_-]+", "-", str(data.get("code") or name).strip()).strip("-").upper()[:120]
    if not code:
        raise ValueError("模板编码不能为空")
    target_portal_type = normalize_portal_type(data.get("targetPortalType") or data.get("portalType") or "department")
    target_module_key = str(data.get("targetModuleKey") or data.get("moduleKey") or "").strip()
    if not module_meta_for_key(target_module_key, target_portal_type):
        raise ValueError("模板绑定板块无效")
    target_content_type = normalize_content_type(data.get("targetContentType") or data.get("contentType") or default_content_type_for_module(target_module_key))
    form_base = {
        "name": name,
        "code": code,
        "description": str(data.get("description") or "").strip()[:1024],
        "targetType": "content_item",
        "targetPortalType": target_portal_type,
        "targetContentType": target_content_type,
        "targetModuleKey": target_module_key,
    }
    schema = normalize_lowcode_schema(data.get("schema") or data.get("schemaJson"), form_base)
    enabled = bool_value(data.get("enabled"), True)
    now = now_iso()
    with db_connect() as conn:
        if form_id:
            current = conn.execute("SELECT * FROM lowcode_forms WHERE id = ?", (form_id,)).fetchone()
            if not current:
                raise ValueError("模板不存在")
            conflict = conn.execute("SELECT id FROM lowcode_forms WHERE code = ? AND id != ? LIMIT 1", (code, form_id)).fetchone()
            if conflict:
                raise ValueError("模板编码已存在")
            conn.execute(
                """
                UPDATE lowcode_forms SET
                    name = ?, code = ?, description = ?, target_type = 'content_item',
                    target_portal_type = ?, target_content_type = ?, target_module_key = ?,
                    enabled = ?, updated_at = ?
                WHERE id = ?
                """,
                (name, code, form_base["description"], target_portal_type, target_content_type, target_module_key, 1 if enabled else 0, now, form_id),
            )
        else:
            conflict = conn.execute("SELECT id FROM lowcode_forms WHERE code = ? LIMIT 1", (code,)).fetchone()
            if conflict:
                raise ValueError("模板编码已存在")
            cursor = conn.execute(
                """
                INSERT INTO lowcode_forms (
                    name, code, description, target_type, target_portal_type,
                    target_content_type, target_module_key, enabled, created_by,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, 'content_item', ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    code,
                    form_base["description"],
                    target_portal_type,
                    target_content_type,
                    target_module_key,
                    1 if enabled else 0,
                    actor.get("username", ADMIN_USERNAME),
                    now,
                    now,
                ),
            )
            form_id = cursor.lastrowid
        conn.execute("UPDATE lowcode_form_versions SET status = 'archived' WHERE form_id = ? AND status = 'active'", (form_id,))
        version_no = latest_lowcode_version_no(conn, form_id) + 1
        conn.execute(
            """
            INSERT INTO lowcode_form_versions (
                form_id, version_no, schema_json, status, created_by, created_at
            )
            VALUES (?, ?, ?, 'active', ?, ?)
            """,
            (form_id, version_no, json_text(schema, {}), actor.get("username", ADMIN_USERNAME), now),
        )
    return get_lowcode_form(form_id)


def lowcode_assets_from_value(value, role="gallery"):
    if value is None:
        return []
    if isinstance(value, list):
        assets = value
    else:
        assets = [
            {"url": line.strip(), "role": role}
            for line in re.split(r"[\r\n]+", str(value or ""))
            if line.strip()
        ]
    normalized = []
    for index, asset in enumerate(assets):
        if isinstance(asset, str):
            asset = {"url": asset, "role": role}
        if not isinstance(asset, dict):
            continue
        normalized_asset = {
            "assetId": int_value(asset.get("assetId") or asset.get("asset_id")) or None,
            "role": str(asset.get("role") or role or "gallery").strip()[:40] or "gallery",
            "title": str(asset.get("title") or "").strip()[:255],
            "caption": str(asset.get("caption") or "").strip()[:512],
            "url": str(asset.get("url") or "").strip()[:2048],
            "sortOrder": int_value(asset.get("sortOrder"), index),
        }
        if normalized_asset["url"] or normalized_asset["assetId"]:
            normalized.append(normalized_asset)
    return normalized


def lowcode_record_payload(form, submitted):
    schema = form.get("schema") or {}
    submitted = submitted if isinstance(submitted, dict) else {}
    fields = schema.get("fields") if isinstance(schema.get("fields"), list) else []
    payload = {
        "moduleKey": form.get("targetModuleKey") or schema.get("moduleKey"),
        "contentType": normalize_content_type(form.get("targetContentType") or schema.get("contentType")),
        "title": "",
        "subtitle": "",
        "summary": "",
        "bodyJson": [],
        "metaJson": {},
        "assets": [],
        "sortOrder": 0,
        "featured": False,
        "enabled": True,
    }
    body_parts = []
    errors = []
    field_keys = {str(field.get("key") or "") for field in fields if isinstance(field, dict)}
    for field in fields:
        key = str(field.get("key") or "")
        if not key:
            continue
        value = submitted.get(key)
        if (value is None or str(value).strip() == "") and field.get("defaultValue") not in (None, ""):
            value = field.get("defaultValue")
        if field.get("required") and (value is None or str(value).strip() == ""):
            errors.append(f"{field.get('label') or key}不能为空")
            continue
        mapping = str(field.get("mapping") or "")
        if mapping == "content_item.title":
            payload["title"] = str(value or "").strip()
        elif mapping == "content_item.subtitle":
            payload["subtitle"] = str(value or "").strip()
        elif mapping == "content_item.summary":
            payload["summary"] = str(value or "").strip()
        elif mapping == "content_item.body_text":
            if str(value or "").strip():
                body_parts.append(str(value or "").strip())
        elif mapping == "content_item.sort_order":
            payload["sortOrder"] = int_value(value)
        elif mapping == "content_item.featured":
            payload["featured"] = bool_value(value)
        elif mapping.startswith("content_item.meta_json."):
            meta_key = mapping.removeprefix("content_item.meta_json.").strip() or field.get("label") or key
            if str(value or "").strip():
                payload["metaJson"][meta_key] = str(value or "").strip()
        elif mapping.startswith("content_item.assets."):
            role = mapping.rsplit(".", 1)[-1] or "gallery"
            payload["assets"].extend(lowcode_assets_from_value(value, role))
    if "bodyText" not in field_keys and submitted.get("bodyText"):
        body_parts.append(str(submitted.get("bodyText") or "").strip())
    if "assets" not in field_keys:
        payload["assets"].extend(lowcode_assets_from_value(submitted.get("assets"), "gallery"))
    if errors:
        raise ValueError("；".join(errors))
    if body_parts:
        payload["bodyJson"] = content_body_json_from_data("\n\n".join(body_parts))
    if not payload["title"]:
        payload["title"] = form.get("name") or "未命名资料"
    if not payload["summary"]:
        payload["summary"] = payload["subtitle"] or (body_parts[0][:120] if body_parts else form.get("description", ""))
    return payload


def row_to_lowcode_record(row):
    if not row:
        return None
    keys = row.keys()
    project_portal_type = normalize_portal_type(row["project_portal_type"] if "project_portal_type" in keys else "department")
    module_key = row["content_module_key"] if "content_module_key" in keys and row["content_module_key"] else ""
    module_meta = module_meta_for_key(module_key, project_portal_type)
    content_type = normalize_content_type(row["content_type"] if "content_type" in keys and row["content_type"] else "article")
    content_status = row["content_review_status"] if "content_review_status" in keys and row["content_review_status"] else ""
    content_code = row["content_code"] if "content_code" in keys and row["content_code"] else ""
    return {
        "id": row["id"],
        "formId": row["form_id"],
        "formVersionId": row["form_version_id"],
        "projectId": row["project_id"],
        "contentItemId": row["content_item_id"],
        "status": row["status"],
        "effectiveStatus": content_status or row["status"],
        "formName": row["form_name"] if "form_name" in keys else "",
        "formCode": row["form_code"] if "form_code" in keys else "",
        "formVersionNo": int_value(row["form_version_no"] if "form_version_no" in keys else 0),
        "contentTitle": row["content_title"] if "content_title" in keys else "",
        "contentCode": content_code,
        "contentModuleKey": module_key,
        "contentModuleLabel": module_meta["label"] if module_meta else module_key,
        "contentType": content_type,
        "contentTypeLabel": content_type_label(content_type),
        "contentReviewStatus": content_status,
        "previewUrl": f"/display?project={row['project_id']}&code={content_code}" if content_code else "",
        "data": json_value(row["data_json"], {}),
        "submittedBy": row["submitted_by"],
        "submittedAt": row["submitted_at"],
        "reviewedBy": row["reviewed_by"],
        "reviewedAt": row["reviewed_at"],
        "reviewNote": row["review_note"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def list_lowcode_records(project_id):
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT
                lowcode_records.*,
                lowcode_forms.name AS form_name,
                lowcode_forms.code AS form_code,
                lowcode_form_versions.version_no AS form_version_no,
                content_items.code AS content_code,
                content_items.title AS content_title,
                content_items.module_key AS content_module_key,
                content_items.content_type AS content_type,
                content_items.review_status AS content_review_status,
                projects.portal_type AS project_portal_type
            FROM lowcode_records
            LEFT JOIN lowcode_forms ON lowcode_forms.id = lowcode_records.form_id
            LEFT JOIN lowcode_form_versions ON lowcode_form_versions.id = lowcode_records.form_version_id
            LEFT JOIN content_items ON content_items.id = lowcode_records.content_item_id
            LEFT JOIN projects ON projects.id = lowcode_records.project_id
            WHERE lowcode_records.project_id = ?
            ORDER BY lowcode_records.submitted_at DESC, lowcode_records.id DESC
            """,
            (project_id,),
        ).fetchall()
    return [row_to_lowcode_record(row) for row in rows]


def submit_lowcode_record(project_id, form_id, data, actor):
    project = get_project(project_id)
    if not project:
        raise ValueError("项目不存在")
    form = get_lowcode_form(form_id)
    if not form or not form.get("enabled"):
        raise ValueError("资料采集模板不存在或已停用")
    project_portal_type = normalize_portal_type(project.get("portalType"))
    if normalize_portal_type(form.get("targetPortalType")) != project_portal_type:
        raise ValueError("资料采集模板不适用于当前门户")
    submitted = data.get("data") if isinstance(data.get("data"), dict) else data
    submitted = dict(submitted or {})
    if isinstance(data.get("assets"), list):
        submitted["assets"] = data.get("assets")
    payload = lowcode_record_payload(form, submitted)
    validate_content_asset_access(payload.get("coverAssetId"), payload.get("assets", []), actor)
    approve_now = actor.get("role") == "admin"
    item = save_content_item(project_id, None, payload, actor, approve_now=approve_now)
    now = now_iso()
    status = "approved" if approve_now else "pending"
    version_id = (form.get("version") or {}).get("id")
    if not version_id:
        raise ValueError("资料采集模板缺少有效版本")
    with db_connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO lowcode_records (
                form_id, form_version_id, project_id, content_item_id, status,
                data_json, submitted_by, submitted_at, reviewed_by, reviewed_at,
                review_note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?)
            """,
            (
                form_id,
                version_id,
                project_id,
                item["id"],
                status,
                json_text({"fields": submitted, "contentItemPayload": payload}, {}),
                actor.get("username", ADMIN_USERNAME),
                now,
                actor.get("username", ADMIN_USERNAME) if approve_now else "",
                now if approve_now else "",
                now,
                now,
            ),
        )
        record_id = cursor.lastrowid
        for index, asset in enumerate(payload.get("assets", [])):
            conn.execute(
                """
                INSERT INTO lowcode_record_assets (
                    record_id, asset_id, role, title, caption, url, sort_order, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    asset.get("assetId"),
                    asset.get("role") or "gallery",
                    asset.get("title") or "",
                    asset.get("caption") or "",
                    asset.get("url") or "",
                    int_value(asset.get("sortOrder"), index),
                    now,
                ),
            )
    return {"record": row_to_lowcode_record({**{"id": record_id}, **{
        "form_id": form_id,
        "form_version_id": version_id,
        "project_id": project_id,
        "content_item_id": item["id"],
        "status": status,
        "data_json": json_text({"fields": submitted, "contentItemPayload": payload}, {}),
        "submitted_by": actor.get("username", ADMIN_USERNAME),
        "submitted_at": now,
        "reviewed_by": actor.get("username", ADMIN_USERNAME) if approve_now else "",
        "reviewed_at": now if approve_now else "",
        "review_note": "",
        "created_at": now,
        "updated_at": now,
    }}), "item": item}


def content_modules_payload(items, portal_type="department"):
    grouped = {module["key"]: [] for module in module_set_for_portal_type(portal_type)}
    for item in items or []:
        key = item.get("moduleKey", "")
        if key in grouped:
            grouped[key].append(item)
    return [
        {
            "key": module["key"],
            "label": module["label"],
            "description": module["description"],
            "items": grouped[module["key"]],
        }
        for module in module_set_for_portal_type(portal_type)
    ]


def content_item_code_conflict(conn, project_id, code, exclude_item_id=None, current_page_id=None):
    if exclude_item_id:
        row = conn.execute(
            "SELECT id FROM content_items WHERE project_id = ? AND code = ? AND id != ? LIMIT 1",
            (project_id, code, exclude_item_id),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM content_items WHERE project_id = ? AND code = ? LIMIT 1",
            (project_id, code),
        ).fetchone()
    if row:
        return "结构化资料编号已存在"
    if current_page_id:
        page_row = conn.execute(
            "SELECT id FROM pages WHERE project_id = ? AND code = ? AND id != ? LIMIT 1",
            (project_id, code, current_page_id),
        ).fetchone()
    else:
        page_row = conn.execute(
            "SELECT id FROM pages WHERE project_id = ? AND code = ? LIMIT 1",
            (project_id, code),
        ).fetchone()
    if page_row:
        return "展示页编号已存在"
    return ""


def unique_content_item_code(conn, project_id, module_key):
    base = f"CI-{str(module_key or 'ITEM').upper()}-{project_id}-{uuid.uuid4().hex[:6].upper()}"
    code = base
    index = 2
    while content_item_code_conflict(conn, project_id, code):
        code = f"{base}-{index}"
        index += 1
    return code


def content_item_payload_from_data(data, current=None, project=None):
    current = current or {}
    project = project or {}
    portal_type = normalize_portal_type(project.get("portalType", "department"))

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    module_key = str(data.get("moduleKey") or current.get("moduleKey") or "").strip()
    if not module_key:
        module_key = module_key_for_category(data.get("category") or current.get("moduleLabel") or "", portal_type)
    if not module_meta_for_key(module_key, portal_type):
        raise ValueError("所属板块无效")
    content_type = normalize_content_type(
        data.get("contentType") or current.get("contentType") or default_content_type_for_module(module_key)
    )
    title = field("title", "未命名资料") or "未命名资料"
    body_json = content_body_json_from_data(
        data.get("bodyJson") if "bodyJson" in data else current.get("bodyJson"),
        data.get("body") or current.get("body") or "",
    )
    meta_json = data.get("metaJson") if "metaJson" in data else data.get("meta")
    if meta_json is None:
        meta_json = current.get("metaJson", {})
    cover_asset_id = int_value(data.get("coverAssetId") if "coverAssetId" in data else current.get("coverAssetId"))
    assets = content_assets_from_data(data.get("assets") if "assets" in data else current.get("assets", []))
    return {
        "code": field("code", current.get("code", "")),
        "moduleKey": module_key,
        "contentType": content_type,
        "title": title[:255],
        "subtitle": field("subtitle")[:512],
        "summary": field("summary", field("subtitle"))[:1024],
        "bodyJson": body_json,
        "metaJson": json_value(meta_json, {}),
        "coverAssetId": cover_asset_id if cover_asset_id > 0 else None,
        "sortOrder": int_value(data.get("sortOrder") if "sortOrder" in data else current.get("sortOrder")),
        "featured": bool_value(data.get("featured"), bool(current.get("featured", False))),
        "enabled": bool_value(data.get("enabled"), bool(current.get("enabled", True))),
        "assets": assets,
    }


def render_content_body_block(block):
    if isinstance(block, str):
        text = block.strip()
        return f"<p>{html_attr(text)}</p>" if text else ""
    if not isinstance(block, dict):
        return ""
    block_type = str(block.get("type") or "paragraph").strip().lower()
    if block_type == "html":
        return sanitize_rich_html(str(block.get("html") or ""))
    if block_type in {"heading", "h2", "title"}:
        return f"<h2>{html_attr(block.get('text') or block.get('title') or '')}</h2>"
    if block_type in {"h3", "subheading"}:
        return f"<h3>{html_attr(block.get('text') or block.get('title') or '')}</h3>"
    if block_type in {"list", "ul"}:
        items = block.get("items") if isinstance(block.get("items"), list) else []
        lis = "".join(f"<li>{html_attr(item)}</li>" for item in items if str(item).strip())
        return f"<ul>{lis}</ul>" if lis else ""
    if block_type in {"quote", "blockquote"}:
        return f"<blockquote>{html_attr(block.get('text') or '')}</blockquote>"
    text = str(block.get("text") or block.get("content") or "").strip()
    return f"<p>{html_attr(text).replace(chr(10), '<br>')}</p>" if text else ""


def content_item_body_html(snapshot, assets):
    body = snapshot.get("bodyJson", [])
    if isinstance(body, dict):
        if isinstance(body.get("blocks"), list):
            body = body["blocks"]
        elif isinstance(body.get("paragraphs"), list):
            body = [{"type": "paragraph", "text": item} for item in body["paragraphs"]]
        else:
            body = [body]
    if not isinstance(body, list):
        body = []
    html = "".join(render_content_body_block(block) for block in body)
    for asset in assets or []:
        url = str(asset.get("url") or "").strip()
        if not url:
            continue
        caption = asset.get("caption") or asset.get("title") or snapshot.get("title", "")
        role = str(asset.get("role") or "").lower()
        if role == "video" or re.search(r"\.(mp4|webm|ogg)(\?|#|$)", url, flags=re.I):
            poster = asset.get("poster") or ""
            html += (
                f'<figure><img src="{html_attr(poster)}" alt="{html_attr(caption)}">'
                f'<figcaption><strong>{html_attr(asset.get("title") or "视频资源")}</strong> '
                f'<a href="{html_attr(url)}">{html_attr(caption or "视频")}</a></figcaption></figure>'
            )
        else:
            html += (
                f'<figure><img src="{html_attr(url)}" alt="{html_attr(caption)}">'
                f'<figcaption>{html_attr(caption)}</figcaption></figure>'
            )
    return sanitize_rich_html(html)


def content_item_cover_url(conn, snapshot, assets):
    cover_asset_id = int_value(snapshot.get("coverAssetId"))
    if cover_asset_id:
        row = conn.execute("SELECT url FROM assets WHERE id = ?", (cover_asset_id,)).fetchone()
        if row and row["url"]:
            return row["url"]
    preferred_roles = {"cover", "portrait", "certificate", "gallery"}
    for asset in assets or []:
        if asset.get("role") in preferred_roles and asset.get("url"):
            return asset["url"]
    for asset in assets or []:
        if asset.get("url") and not re.search(r"\.(mp4|webm|ogg)(\?|#|$)", asset["url"], flags=re.I):
            return asset["url"]
    return ""


def replace_content_item_assets(conn, content_item_id, assets):
    conn.execute("DELETE FROM content_item_assets WHERE content_item_id = ?", (content_item_id,))
    for index, asset in enumerate(assets or []):
        conn.execute(
            """
            INSERT INTO content_item_assets (
                content_item_id, asset_id, role, title, caption, url, sort_order, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                content_item_id,
                asset.get("assetId"),
                asset.get("role", "gallery"),
                asset.get("title", ""),
                asset.get("caption", ""),
                asset.get("url", ""),
                int_value(asset.get("sortOrder"), index),
                now_iso(),
            ),
        )


def sync_content_item_page(conn, project_id, content_item_id, snapshot, actor):
    row = conn.execute("SELECT page_id FROM content_items WHERE id = ?", (content_item_id,)).fetchone()
    page_id = row["page_id"] if row and row["page_id"] else None
    project = get_project(project_id) or {}
    module_meta = module_meta_for_key(snapshot["moduleKey"], project.get("portalType", "department"))
    category = module_meta["label"] if module_meta else snapshot["moduleKey"]
    assets = content_item_asset_rows(conn, content_item_id)
    body_html = content_item_body_html(snapshot, assets)
    image_url = content_item_cover_url(conn, snapshot, assets)
    page_snapshot = {
        "code": snapshot["code"],
        "category": category,
        "source": "结构化资料",
        "publishedAt": now_iso()[:10],
        "title": snapshot["title"],
        "subtitle": snapshot.get("summary") or snapshot.get("subtitle", ""),
        "body": body_html,
        "imageUrl": image_url,
        "contentType": snapshot["contentType"],
        "accent": project.get("accent", "#0f766e"),
        "enabled": bool(snapshot.get("enabled", True)),
    }
    existing = None
    if page_id:
        existing = conn.execute(
            "SELECT id FROM pages WHERE id = ? AND project_id = ?",
            (page_id, project_id),
        ).fetchone()
    if not existing:
        existing = conn.execute(
            "SELECT id FROM pages WHERE project_id = ? AND code = ?",
            (project_id, snapshot["code"]),
        ).fetchone()
    page_id = apply_page_snapshot(conn, project_id, existing["id"] if existing else None, page_snapshot, actor)
    conn.execute("UPDATE content_items SET page_id = ? WHERE id = ?", (page_id, content_item_id))
    return page_id


def content_item_snapshot_from_row(conn, row):
    item = row_to_content_item(row, content_item_asset_rows(conn, row["id"])) if row else None
    if not item:
        return {}
    return {
        "code": item["code"],
        "moduleKey": item["moduleKey"],
        "contentType": item["contentType"],
        "title": item["title"],
        "subtitle": item["subtitle"],
        "summary": item["summary"],
        "bodyJson": item["bodyJson"],
        "metaJson": item["metaJson"],
        "coverAssetId": item["coverAssetId"],
        "sortOrder": item["sortOrder"],
        "featured": item["featured"],
        "enabled": item["enabled"],
        "assets": item["assets"],
    }


def write_content_item_version(conn, project_id, content_item_id, snapshot, actor, status="approved", operation="upsert"):
    current = {}
    if content_item_id:
        row = conn.execute("SELECT * FROM content_items WHERE id = ?", (content_item_id,)).fetchone()
        current = content_item_snapshot_from_row(conn, row)
    changes = summarize_changes(current, snapshot)
    cursor = conn.execute(
        """
        INSERT INTO content_item_versions (
            content_item_id, project_id, operation, status, snapshot_json,
            submitted_by, submitted_at, reviewed_by, reviewed_at, changes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            content_item_id,
            project_id,
            operation,
            status,
            json_text(snapshot, {}),
            actor.get("username", ADMIN_USERNAME),
            now_iso(),
            actor.get("username", ADMIN_USERNAME) if status == "approved" else "",
            now_iso() if status == "approved" else "",
            changes,
        ),
    )
    return cursor.lastrowid


def apply_content_item_snapshot(conn, project_id, content_item_id, snapshot, actor):
    now = now_iso()
    if content_item_id:
        conn.execute(
            """
            UPDATE content_items SET
                code = ?, module_key = ?, content_type = ?, title = ?, subtitle = ?,
                summary = ?, body_json = ?, meta_json = ?, cover_asset_id = ?,
                sort_order = ?, featured = ?, enabled = ?, review_status = 'approved',
                pending_version_id = NULL, reviewed_by = ?, review_note = '', updated_at = ?
            WHERE id = ? AND project_id = ?
            """,
            (
                snapshot["code"],
                snapshot["moduleKey"],
                snapshot["contentType"],
                snapshot["title"],
                snapshot["subtitle"],
                snapshot["summary"],
                json_text(snapshot["bodyJson"], []),
                json_text(snapshot["metaJson"], {}),
                snapshot.get("coverAssetId"),
                int_value(snapshot.get("sortOrder")),
                1 if snapshot.get("featured") else 0,
                1 if snapshot.get("enabled", True) else 0,
                actor.get("username", ADMIN_USERNAME),
                now,
                content_item_id,
                project_id,
            ),
        )
    else:
        cursor = conn.execute(
            """
            INSERT INTO content_items (
                project_id, code, module_key, content_type, title, subtitle,
                summary, body_json, meta_json, cover_asset_id, sort_order,
                featured, enabled, review_status, submitted_by, reviewed_by,
                review_note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?, ?, '', ?, ?)
            """,
            (
                project_id,
                snapshot["code"],
                snapshot["moduleKey"],
                snapshot["contentType"],
                snapshot["title"],
                snapshot["subtitle"],
                snapshot["summary"],
                json_text(snapshot["bodyJson"], []),
                json_text(snapshot["metaJson"], {}),
                snapshot.get("coverAssetId"),
                int_value(snapshot.get("sortOrder")),
                1 if snapshot.get("featured") else 0,
                1 if snapshot.get("enabled", True) else 0,
                actor.get("username", ADMIN_USERNAME),
                actor.get("username", ADMIN_USERNAME),
                now,
                now,
            ),
        )
        content_item_id = cursor.lastrowid
    replace_content_item_assets(conn, content_item_id, snapshot.get("assets", []))
    sync_content_item_page(conn, project_id, content_item_id, snapshot, actor)
    return content_item_id


def save_content_item(project_id, content_item_id, data, actor, approve_now=False):
    project = get_project(project_id)
    if not project:
        raise ValueError("项目不存在")
    current = get_content_item(project_id, content_item_id) if content_item_id else {}
    if content_item_id and not current:
        raise ValueError("资料不存在")
    snapshot = content_item_payload_from_data(data, current, project)
    with db_connect() as conn:
        if not snapshot["code"]:
            snapshot["code"] = unique_content_item_code(conn, project_id, snapshot["moduleKey"])
        conflict = content_item_code_conflict(
            conn,
            project_id,
            snapshot["code"],
            content_item_id or None,
            current.get("pageId") if current else None,
        )
        if conflict:
            raise ValueError(conflict)
    validate_content_asset_access(snapshot.get("coverAssetId"), snapshot.get("assets", []), actor)
    with db_connect() as conn:
        if approve_now:
            item_id = apply_content_item_snapshot(conn, project_id, content_item_id or None, snapshot, actor)
            version_id = write_content_item_version(conn, project_id, item_id, snapshot, actor, "approved", "upsert")
            conn.execute("UPDATE content_item_versions SET content_item_id = ? WHERE id = ?", (item_id, version_id))
        else:
            now = now_iso()
            if content_item_id:
                item_id = content_item_id
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO content_items (
                        project_id, code, module_key, content_type, title, subtitle,
                        summary, body_json, meta_json, cover_asset_id, sort_order,
                        featured, enabled, review_status, submitted_by, reviewed_by,
                        review_note, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'pending', ?, '', '', ?, ?)
                    """,
                    (
                        project_id,
                        snapshot["code"],
                        snapshot["moduleKey"],
                        snapshot["contentType"],
                        snapshot["title"],
                        snapshot["subtitle"],
                        snapshot["summary"],
                        json_text(snapshot["bodyJson"], []),
                        json_text(snapshot["metaJson"], {}),
                        snapshot.get("coverAssetId"),
                        int_value(snapshot.get("sortOrder")),
                        1 if snapshot.get("featured") else 0,
                        actor.get("username", ""),
                        now,
                        now,
                    ),
                )
                item_id = cursor.lastrowid
            version_id = write_content_item_version(conn, project_id, item_id, snapshot, actor, "pending", "upsert")
            conn.execute(
                """
                UPDATE content_items SET review_status = 'pending', pending_version_id = ?,
                    submitted_by = ?, review_note = '', updated_at = ?
                WHERE id = ?
                """,
                (version_id, actor.get("username", ""), now_iso(), item_id),
            )
    return get_content_item(project_id, item_id)


def delete_content_item(project_id, content_item_id, actor, approve_now=False):
    item = get_content_item(project_id, content_item_id)
    if not item:
        return None
    snapshot = {
        "code": item["code"],
        "moduleKey": item["moduleKey"],
        "contentType": item["contentType"],
        "title": item["title"],
        "subtitle": item["subtitle"],
        "summary": item["summary"],
        "bodyJson": item["bodyJson"],
        "metaJson": item["metaJson"],
        "coverAssetId": item["coverAssetId"],
        "sortOrder": item["sortOrder"],
        "featured": item["featured"],
        "enabled": False,
        "assets": item["assets"],
    }
    with db_connect() as conn:
        if approve_now:
            if item.get("pageId"):
                conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (item["pageId"],))
                conn.execute(
                    "UPDATE pages SET enabled = 0, review_status = 'deleted', pending_version_id = NULL, updated_at = ? WHERE id = ?",
                    (now_iso(), item["pageId"]),
                )
            conn.execute(
                """
                UPDATE content_items SET enabled = 0, review_status = 'deleted',
                    pending_version_id = NULL, reviewed_by = ?, review_note = '', updated_at = ?
                WHERE id = ? AND project_id = ?
                """,
                (actor.get("username", ADMIN_USERNAME), now_iso(), content_item_id, project_id),
            )
            write_content_item_version(conn, project_id, content_item_id, snapshot, actor, "approved", "delete")
        else:
            version_id = write_content_item_version(conn, project_id, content_item_id, snapshot, actor, "pending", "delete")
            conn.execute(
                """
                UPDATE content_items SET review_status = 'pending_delete', pending_version_id = ?,
                    submitted_by = ?, review_note = '', updated_at = ?
                WHERE id = ?
                """,
                (version_id, actor.get("username", ""), now_iso(), content_item_id),
            )
    return item


def row_to_content_item_version(row):
    if not row:
        return None
    snapshot = json_value(row["snapshot_json"], {})
    current_item = get_content_item_by_id(row["content_item_id"]) if row["content_item_id"] else None
    current = {
        "code": current_item.get("code", ""),
        "moduleKey": current_item.get("moduleKey", ""),
        "contentType": current_item.get("contentType", ""),
        "title": current_item.get("title", ""),
        "subtitle": current_item.get("subtitle", ""),
        "summary": current_item.get("summary", ""),
        "bodyJson": current_item.get("bodyJson", []),
        "metaJson": current_item.get("metaJson", {}),
        "coverAssetId": current_item.get("coverAssetId"),
        "sortOrder": current_item.get("sortOrder", 0),
        "featured": current_item.get("featured", False),
        "enabled": current_item.get("enabled", True),
        "assets": current_item.get("assets", []),
    } if current_item else {}
    code = snapshot.get("code") or row["content_item_id"] or ""
    return {
        "id": row["id"],
        "contentItemId": row["content_item_id"],
        "projectId": row["project_id"],
        "projectName": row["project_name"] if "project_name" in row.keys() else "",
        "operation": row["operation"],
        "status": row["status"],
        "snapshot": snapshot,
        "current": current,
        "diffs": review_diffs(current, snapshot),
        "previewUrl": f"/display?project={row['project_id']}&code={code}&preview=review&reviewVersion={row['id']}",
        "submittedBy": row["submitted_by"],
        "submittedAt": row["submitted_at"],
        "reviewedBy": row["reviewed_by"],
        "reviewedAt": row["reviewed_at"],
        "reviewNote": row["review_note"],
        "changes": row["changes"],
    }


def approve_content_item_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM content_item_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        version = row_to_content_item_version(row)
        snapshot = version["snapshot"]
        if version["operation"] == "delete":
            item = get_content_item_by_id(version["contentItemId"])
            if item and item.get("pageId"):
                conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (item["pageId"],))
                conn.execute(
                    "UPDATE pages SET enabled = 0, review_status = 'deleted', pending_version_id = NULL, updated_at = ? WHERE id = ?",
                    (now_iso(), item["pageId"]),
                )
            conn.execute(
                """
                UPDATE content_items SET enabled = 0, review_status = 'deleted',
                    pending_version_id = NULL, reviewed_by = ?, review_note = ?, updated_at = ?
                WHERE id = ?
                """,
                (actor["username"], note, now_iso(), version["contentItemId"]),
            )
            item_id = version["contentItemId"]
        else:
            item_id = apply_content_item_snapshot(conn, version["projectId"], version["contentItemId"], snapshot, actor)
            conn.execute("UPDATE content_item_versions SET content_item_id = ? WHERE id = ?", (item_id, version_id))
        conn.execute(
            """
            UPDATE content_item_versions SET status = 'approved', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
        conn.execute(
            """
            UPDATE lowcode_records SET status = 'approved', reviewed_by = ?,
                reviewed_at = ?, review_note = ?, updated_at = ?
            WHERE content_item_id = ?
            """,
            (actor["username"], now_iso(), note, now_iso(), item_id),
        )
    return get_content_item_by_id(item_id)


def reject_content_item_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM content_item_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        conn.execute(
            """
            UPDATE content_item_versions SET status = 'rejected', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
        conn.execute(
            """
            UPDATE content_items SET review_status = 'rejected', review_note = ?,
                reviewed_by = ?, updated_at = ?
            WHERE pending_version_id = ?
            """,
            (note, actor["username"], now_iso(), version_id),
        )
        conn.execute(
            """
            UPDATE lowcode_records SET status = 'rejected', reviewed_by = ?,
                reviewed_at = ?, review_note = ?, updated_at = ?
            WHERE content_item_id IN (
                SELECT content_item_id FROM content_item_versions WHERE id = ?
            )
            """,
            (actor["username"], now_iso(), note, now_iso(), version_id),
        )
    return row_to_content_item_version(row)


def add_content_item_asset(content_item_id, data, actor):
    item = get_content_item_by_id(content_item_id)
    if not item:
        return None
    project = get_project(item["projectId"])
    if not project_accessible(project, actor):
        return None
    if actor.get("role") != "admin":
        raise ValueError("素材关联直接修改需要管理员权限，请通过资料草稿提交")
    asset_id = int_value(data.get("assetId") or data.get("asset_id"))
    if asset_id:
        validate_content_asset_access(asset_id, [], actor)
    payload = content_assets_from_data([{**data, "assetId": asset_id or None}])[0]
    with db_connect() as conn:
        conn.execute(
            """
            INSERT INTO content_item_assets (
                content_item_id, asset_id, role, title, caption, url, sort_order, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                content_item_id,
                payload.get("assetId"),
                payload.get("role", "gallery"),
                payload.get("title", ""),
                payload.get("caption", ""),
                payload.get("url", ""),
                int_value(payload.get("sortOrder")),
                now_iso(),
            ),
        )
        row = conn.execute("SELECT * FROM content_items WHERE id = ?", (content_item_id,)).fetchone()
        snapshot = content_item_snapshot_from_row(conn, row)
        if item.get("reviewStatus") == "approved":
            sync_content_item_page(conn, item["projectId"], content_item_id, snapshot, actor)
    return get_content_item_by_id(content_item_id)


def reorder_content_item_assets(content_item_id, assets, actor):
    item = get_content_item_by_id(content_item_id)
    if not item:
        return None
    project = get_project(item["projectId"])
    if not project_accessible(project, actor):
        return None
    if actor.get("role") != "admin":
        raise ValueError("素材排序直接修改需要管理员权限，请通过资料草稿提交")
    with db_connect() as conn:
        for index, asset in enumerate(assets or []):
            relation_id = int_value(asset.get("id"))
            sort_order = int_value(asset.get("sortOrder"), index)
            if relation_id:
                conn.execute(
                    "UPDATE content_item_assets SET sort_order = ? WHERE id = ? AND content_item_id = ?",
                    (sort_order, relation_id, content_item_id),
                )
        row = conn.execute("SELECT * FROM content_items WHERE id = ?", (content_item_id,)).fetchone()
        snapshot = content_item_snapshot_from_row(conn, row)
        if item.get("reviewStatus") == "approved":
            sync_content_item_page(conn, item["projectId"], content_item_id, snapshot, actor)
    return get_content_item_by_id(content_item_id)


def delete_content_item_asset(content_item_id, asset_ref, actor):
    item = get_content_item_by_id(content_item_id)
    if not item:
        return None
    project = get_project(item["projectId"])
    if not project_accessible(project, actor):
        return None
    if actor.get("role") != "admin":
        raise ValueError("素材关联直接删除需要管理员权限，请通过资料草稿提交")
    ref = int_value(asset_ref)
    with db_connect() as conn:
        row = conn.execute(
            "SELECT id FROM content_item_assets WHERE id = ? AND content_item_id = ?",
            (ref, content_item_id),
        ).fetchone()
        if row:
            conn.execute("DELETE FROM content_item_assets WHERE id = ?", (row["id"],))
        else:
            conn.execute(
                "DELETE FROM content_item_assets WHERE asset_id = ? AND content_item_id = ?",
                (ref, content_item_id),
            )
        item_row = conn.execute("SELECT * FROM content_items WHERE id = ?", (content_item_id,)).fetchone()
        snapshot = content_item_snapshot_from_row(conn, item_row)
        if item.get("reviewStatus") == "approved":
            sync_content_item_page(conn, item["projectId"], content_item_id, snapshot, actor)
    return get_content_item_by_id(content_item_id)


def admin_dashboard(user=None):
    user = user or {"role": "admin", "username": ""}
    owner_where = ""
    owner_params = []
    scan_owner_where = ""
    scan_owner_params = []
    if user.get("role") != "admin":
        owner_where = "WHERE projects.owner_username = ?"
        owner_params.append(user.get("username", ""))
        scan_owner_where = "WHERE projects.owner_username = ?"
        scan_owner_params.append(user.get("username", ""))
    with db_connect() as conn:
        project_count = conn.execute(f"SELECT COUNT(*) AS value FROM projects {owner_where}", owner_params).fetchone()["value"]
        page_count = conn.execute(
            f"SELECT COUNT(*) AS value FROM pages JOIN projects ON projects.id = pages.project_id {owner_where}",
            owner_params,
        ).fetchone()["value"]
        enabled_page_count = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.enabled = 1 AND pages.review_status = 'approved'
            """,
            owner_params,
        ).fetchone()["value"]
        pending_count = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.review_status IN ('pending','pending_delete')
            """,
            owner_params,
        ).fetchone()["value"]
        rejected_count = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.review_status = 'rejected'
            """,
            owner_params,
        ).fetchone()["value"]
        if user.get("role") == "admin":
            scan_count = conn.execute("SELECT COUNT(*) AS value FROM scans").fetchone()["value"]
            today_scan_count = conn.execute(
                "SELECT COUNT(*) AS value FROM scans WHERE substr(created_at, 1, 10) = ?",
                (now_iso()[:10],),
            ).fetchone()["value"]
        else:
            scan_count = conn.execute(
                """
                SELECT COUNT(*) AS value
                FROM scans
                JOIN projects ON projects.id = scans.project_id
                WHERE projects.owner_username = ?
                """,
                scan_owner_params,
            ).fetchone()["value"]
            today_scan_count = conn.execute(
                """
                SELECT COUNT(*) AS value
                FROM scans
                JOIN projects ON projects.id = scans.project_id
                WHERE projects.owner_username = ? AND substr(scans.created_at, 1, 10) = ?
                """,
                (*scan_owner_params, now_iso()[:10]),
            ).fetchone()["value"]
        deployed = conn.execute(
            f"""
            SELECT
                MAX(CASE WHEN deployed = 1 THEN name ELSE '' END) AS welcome_name,
                MAX(CASE WHEN content_deployed = 1 THEN name ELSE '' END) AS content_name
            FROM projects
            {owner_where}
            """,
            owner_params,
        ).fetchone()
        categories = conn.execute(
            f"""
            SELECT category, COUNT(*) AS count
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where}
            GROUP BY category
            ORDER BY count DESC, category
            LIMIT 8
            """,
            owner_params,
        ).fetchall()
        recent_scans = conn.execute(
            f"""
            SELECT scans.id, scans.code, scans.raw_url, scans.created_at, pages.title, projects.name AS project_name
            FROM scans
            LEFT JOIN projects ON projects.id = scans.project_id
            LEFT JOIN pages ON pages.project_id = scans.project_id AND pages.code = scans.code
            {scan_owner_where}
            ORDER BY scans.created_at DESC, scans.id DESC
            LIMIT 8
            """,
            scan_owner_params,
        ).fetchall()
        recent_projects = conn.execute(
            f"""
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled,
                   COUNT(pages.id) AS page_count, 0 AS scan_count, 0 AS pending_page_count
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            LEFT JOIN pages ON pages.project_id = p.id
            {owner_where.replace('projects.', 'p.')}
            GROUP BY p.id
            ORDER BY p.updated_at DESC, p.id DESC
            LIMIT 6
            """,
            owner_params,
        ).fetchall()

    return {
        "summary": {
            "projects": int(project_count or 0),
            "pages": int(page_count or 0),
            "enabledPages": int(enabled_page_count or 0),
            "pendingPages": int(pending_count or 0),
            "rejectedPages": int(rejected_count or 0),
            "scans": int(scan_count or 0),
            "todayScans": int(today_scan_count or 0),
            "welcomeDeployed": deployed["welcome_name"] or "",
            "contentDeployed": deployed["content_name"] or "",
            "clients": len(SSE_CLIENTS),
        },
        "categories": [{"name": row["category"] or "未分类", "count": row["count"]} for row in categories],
        "recentScans": [
            {
                "id": row["id"],
                "code": row["code"],
                "url": row["raw_url"],
                "title": row["title"] or "",
                "projectName": row["project_name"] or "",
                "createdAt": row["created_at"],
            }
            for row in recent_scans
        ],
        "recentProjects": [row_to_project(row) for row in recent_projects],
        "logs": list_admin_logs(8) if user.get("role") == "admin" else list_admin_logs(8, username=user.get("username", "")),
        "operations": operations_summary(user),
    }


def upsert_project(project_id, data):
    current = get_project(project_id) if project_id else None
    current = current or {}

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    project = {
        "name": field("name", "新的学校大屏项目") or "新的学校大屏项目",
        "portal_type": normalize_portal_type(field("portalType", current.get("portalType", "department"))),
        "portal_slug": normalize_portal_slug(field("portalSlug", current.get("portalSlug", ""))),
        "idle_kicker": field("idleKicker", "学校简介"),
        "idle_title": field("idleTitle", "欢迎来到毕节职业技术学院"),
        "idle_copy": field("idleCopy", DEFAULT_DISPLAY_CONFIG["summaryCopy"]),
        "welcome_kicker": field("welcomeKicker", "Welcome"),
        "welcome_title": field("welcomeTitle", "欢迎参观 {title}"),
        "welcome_subtitle": field("welcomeSubtitle", "即将进入展示页面"),
        "default_image_url": field("defaultImageUrl", "/static/expo-stage.png") or "/static/expo-stage.png",
        "accent": field("accent", "#f59a13") or "#f59a13",
        "display_config": display_config_json(
            data.get("displayConfig") if "displayConfig" in data else current.get("displayConfig", {})
        ),
        "updated_at": now_iso(),
    }
    if project["portal_type"] == "school":
        project["portal_slug"] = ""

    with db_connect() as conn:
        if project_id:
            conn.execute(
                """
                UPDATE projects SET
                    name = ?, portal_type = ?, portal_slug = ?, idle_kicker = ?, idle_title = ?, idle_copy = ?,
                    welcome_kicker = ?, welcome_title = ?, welcome_subtitle = ?,
                    default_image_url = ?, accent = ?, display_config = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    project["name"],
                    project["portal_type"],
                    project["portal_slug"],
                    project["idle_kicker"],
                    project["idle_title"],
                    project["idle_copy"],
                    project["welcome_kicker"],
                    project["welcome_title"],
                    project["welcome_subtitle"],
                    project["default_image_url"],
                    project["accent"],
                    project["display_config"],
                    project["updated_at"],
                    project_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO projects (
                    name, portal_type, portal_slug, idle_kicker, idle_title, idle_copy, welcome_kicker,
                    welcome_title, welcome_subtitle, default_image_url, accent, display_config, deployed, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    project["name"],
                    project["portal_type"],
                    project["portal_slug"],
                    project["idle_kicker"],
                    project["idle_title"],
                    project["idle_copy"],
                    project["welcome_kicker"],
                    project["welcome_title"],
                    project["welcome_subtitle"],
                    project["default_image_url"],
                    project["accent"],
                    project["display_config"],
                    project["updated_at"],
                ),
            )
            project_id = cursor.lastrowid
    return get_project(project_id)


def summarize_changes(before, after):
    before = before or {}
    after = after or {}
    changed = []
    for key in sorted(set(before.keys()) | set(after.keys())):
        if before.get(key) != after.get(key):
            changed.append(key)
    return ",".join(changed[:30])


REVIEW_FIELD_LABELS = {
    "name": "项目名称",
    "portalType": "门户类型",
    "portalSlug": "门户路由",
    "ownerUsername": "归属账号",
    "idleKicker": "欢迎页小标题",
    "idleTitle": "欢迎页标题",
    "idleCopy": "欢迎页简介",
    "welcomeKicker": "进入页小标题",
    "welcomeTitle": "进入页标题",
    "welcomeSubtitle": "进入页副标题",
    "defaultImageUrl": "默认图片",
    "accent": "主题色",
    "displayConfig": "展示配置",
    "code": "编号",
    "category": "栏目",
    "source": "来源",
    "publishedAt": "发布日期",
    "title": "标题",
    "subtitle": "副标题",
    "summary": "摘要",
    "body": "正文",
    "imageUrl": "图片",
    "contentType": "资料类型",
    "moduleKey": "标准板块",
    "bodyJson": "结构化正文",
    "metaJson": "类型字段",
    "coverAssetId": "封面素材",
    "sortOrder": "排序",
    "featured": "重点展示",
    "assets": "资料素材",
    "enabled": "启用状态",
}


def review_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, bool):
        return "是" if value else "否"
    return "" if value is None else str(value)


def review_diffs(before, after):
    before = before or {}
    after = after or {}
    keys = [key for key in REVIEW_FIELD_LABELS if key in before or key in after]
    keys.extend(sorted((set(before.keys()) | set(after.keys())) - set(keys)))
    diffs = []
    for key in keys:
        before_value = review_value(before.get(key))
        after_value = review_value(after.get(key))
        diffs.append(
            {
                "field": key,
                "label": REVIEW_FIELD_LABELS.get(key, key),
                "before": before_value,
                "after": after_value,
                "changed": before_value != after_value,
            }
        )
    return diffs


def project_public_payload(project):
    portal_type = normalize_portal_type(project.get("portalType", "department"))
    portal_slug = normalize_portal_slug(project.get("portalSlug", ""))
    return {
        "name": project.get("name", ""),
        "portalType": portal_type,
        "portalSlug": "" if portal_type == "school" else portal_slug,
        "ownerUsername": project.get("ownerUsername", ADMIN_USERNAME),
        "idleKicker": project.get("idleKicker", ""),
        "idleTitle": project.get("idleTitle", ""),
        "idleCopy": project.get("idleCopy", ""),
        "welcomeKicker": project.get("welcomeKicker", "Welcome"),
        "welcomeTitle": project.get("welcomeTitle", "Welcome to {title}"),
        "welcomeSubtitle": project.get("welcomeSubtitle", ""),
        "defaultImageUrl": project.get("defaultImageUrl", ""),
        "accent": project.get("accent", "#f59a13"),
        "displayConfig": project.get("displayConfig", {}),
    }


def page_public_payload(page):
    page = page or {}
    return {
        "code": page.get("code", ""),
        "category": page.get("category", DEFAULT_PAGE_CATEGORY),
        "source": page.get("source", DEFAULT_PAGE_SOURCE),
        "publishedAt": page.get("publishedAt", ""),
        "title": page.get("title", ""),
        "subtitle": page.get("subtitle", ""),
        "body": page.get("body", ""),
        "imageUrl": page.get("imageUrl", ""),
        "contentType": normalize_content_type(page.get("contentType", "article")),
        "accent": page.get("accent", "#0f766e"),
        "enabled": bool(page.get("enabled", True)),
    }


def project_payload_from_data(data, current=None):
    current = current or {}

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    display_config = data.get("displayConfig") if "displayConfig" in data else current.get("displayConfig", {})
    portal_type = normalize_portal_type(field("portalType", current.get("portalType", "department")))
    portal_slug = normalize_portal_slug(field("portalSlug", current.get("portalSlug", "")))
    if portal_type == "school":
        portal_slug = ""
    return {
        "name": field("name", "New display project") or "New display project",
        "portal_type": portal_type,
        "portal_slug": portal_slug,
        "owner_username": field("ownerUsername", current.get("ownerUsername", ADMIN_USERNAME)) or ADMIN_USERNAME,
        "idle_kicker": field("idleKicker", "School intro"),
        "idle_title": field("idleTitle", DEFAULT_PROJECT_NAME),
        "idle_copy": field("idleCopy", DEFAULT_DISPLAY_CONFIG["summaryCopy"]),
        "welcome_kicker": field("welcomeKicker", "Welcome"),
        "welcome_title": field("welcomeTitle", "Welcome to {title}"),
        "welcome_subtitle": field("welcomeSubtitle", "Opening display page"),
        "default_image_url": field("defaultImageUrl", "/static/expo-stage.png") or "/static/expo-stage.png",
        "accent": field("accent", "#f59a13") or "#f59a13",
        "display_config": display_config_json(display_config),
        "updated_at": now_iso(),
    }


def project_payload_to_public(payload):
    portal_type = normalize_portal_type(payload.get("portal_type", "department"))
    portal_slug = normalize_portal_slug(payload.get("portal_slug", ""))
    return {
        "name": payload["name"],
        "portalType": portal_type,
        "portalSlug": "" if portal_type == "school" else portal_slug,
        "ownerUsername": payload["owner_username"],
        "idleKicker": payload["idle_kicker"],
        "idleTitle": payload["idle_title"],
        "idleCopy": payload["idle_copy"],
        "welcomeKicker": payload["welcome_kicker"],
        "welcomeTitle": payload["welcome_title"],
        "welcomeSubtitle": payload["welcome_subtitle"],
        "defaultImageUrl": payload["default_image_url"],
        "accent": payload["accent"],
        "displayConfig": normalize_display_config(payload["display_config"]),
    }


def save_project(project_id, data, actor=None):
    actor = actor or {"username": ADMIN_USERNAME}
    current = get_project(project_id) if project_id else None
    current = current or {}
    payload = project_payload_from_data(data, current)
    before = project_public_payload(current)
    after = project_payload_to_public(payload)
    with db_connect() as conn:
        if project_id:
            conn.execute(
                """
                UPDATE projects SET
                    name = ?, portal_type = ?, portal_slug = ?, owner_username = ?, idle_kicker = ?, idle_title = ?, idle_copy = ?,
                    welcome_kicker = ?, welcome_title = ?, welcome_subtitle = ?,
                    default_image_url = ?, accent = ?, display_config = ?,
                    config_status = 'approved', pending_config_version_id = NULL, updated_at = ?
                WHERE id = ?
                """,
                (
                    payload["name"],
                    payload["portal_type"],
                    payload["portal_slug"],
                    payload["owner_username"],
                    payload["idle_kicker"],
                    payload["idle_title"],
                    payload["idle_copy"],
                    payload["welcome_kicker"],
                    payload["welcome_title"],
                    payload["welcome_subtitle"],
                    payload["default_image_url"],
                    payload["accent"],
                    payload["display_config"],
                    payload["updated_at"],
                    project_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO projects (
                    name, portal_type, portal_slug, owner_username, idle_kicker, idle_title, idle_copy, welcome_kicker,
                    welcome_title, welcome_subtitle, default_image_url, accent, display_config,
                    deployed, content_deployed, config_status, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 'approved', ?)
                """,
                (
                    payload["name"],
                    payload["portal_type"],
                    payload["portal_slug"],
                    payload["owner_username"],
                    payload["idle_kicker"],
                    payload["idle_title"],
                    payload["idle_copy"],
                    payload["welcome_kicker"],
                    payload["welcome_title"],
                    payload["welcome_subtitle"],
                    payload["default_image_url"],
                    payload["accent"],
                    payload["display_config"],
                    payload["updated_at"],
                ),
            )
            project_id = cursor.lastrowid
        conn.execute(
            """
            INSERT INTO project_versions (
                project_id, status, snapshot, submitted_by, submitted_at,
                reviewed_by, reviewed_at, changes
            )
            VALUES (?, 'approved', ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                json.dumps(after, ensure_ascii=False),
                actor.get("username", ADMIN_USERNAME),
                now_iso(),
                actor.get("username", ADMIN_USERNAME),
                now_iso(),
                summarize_changes(before, after),
            ),
        )
    return get_project(project_id)


def submit_project_config(project_id, data, user):
    project = get_project(project_id)
    if not project:
        return None
    before = project_public_payload(project)
    payload = project_payload_from_data(data, project)
    proposed = project_payload_to_public(payload)
    proposed["ownerUsername"] = project.get("ownerUsername", ADMIN_USERNAME)
    changes = summarize_changes(before, proposed)
    with db_connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO project_versions (
                project_id, status, snapshot, submitted_by, submitted_at, changes
            )
            VALUES (?, 'pending', ?, ?, ?, ?)
            """,
            (project_id, json.dumps(proposed, ensure_ascii=False), user["username"], now_iso(), changes),
        )
        version_id = cursor.lastrowid
        conn.execute(
            "UPDATE projects SET config_status = 'pending', pending_config_version_id = ?, updated_at = ? WHERE id = ?",
            (version_id, now_iso(), project_id),
        )
    return get_project(project_id)


def deploy_project_check(project_id):
    result = {"ok": True, "projectId": project_id, "errors": [], "warnings": []}
    with db_connect() as conn:
        row = conn.execute("SELECT id, portal_type, config_status FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        result["ok"] = False
        result["errors"].append("项目不存在")
    elif normalize_portal_type(row["portal_type"]) != "school":
        result["ok"] = False
        result["errors"].append("只有学校门户可发布为欢迎页")
    elif row["config_status"] == "pending":
        result["ok"] = False
        result["errors"].append("项目配置正在等待审核")
    return result


def deploy_project(project_id):
    check = deploy_project_check(project_id)
    if not check["ok"]:
        raise ValueError("; ".join(check["errors"]))
    with db_connect() as conn:
        conn.execute("UPDATE projects SET deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (project_id,))
    return get_project(project_id)


def upload_url_to_key(url):
    url = str(url or "").strip()
    if not url:
        return ""
    parsed = urlparse(url)
    path = parsed.path if parsed.scheme else url
    if path.startswith("/uploads/"):
        return path.removeprefix("/uploads/").lstrip("/")
    public_base = os.environ.get("ASSET_PUBLIC_BASE_URL", "").strip().rstrip("/")
    if public_base and url.startswith(public_base + "/"):
        return url.removeprefix(public_base + "/").lstrip("/")
    return ""


def local_upload_missing(url):
    if asset_storage_backend() != "local":
        return False
    key = upload_url_to_key(url)
    if not key:
        return False
    target = (UPLOAD_DIR / key).resolve()
    root = UPLOAD_DIR.resolve()
    if root not in target.parents and target != root:
        return True
    return not target.exists()


def referenced_urls_from_text(text):
    text = str(text or "")
    urls = set(re.findall(r"""(?:src|href)=["']([^"']+)["']""", text, flags=re.I))
    urls.update(re.findall(r"""(?<![\w/])(/uploads/[^\s"'<>),]+)""", text))
    return urls


def page_asset_urls(page):
    urls = set()
    if page.get("imageUrl"):
        urls.add(page["imageUrl"])
    urls.update(referenced_urls_from_text(page.get("body", "")))
    return urls


def pages_by_ids_for_coverage(conn, project_id, page_ids, portal_type="department"):
    ids = [int(page_id) for page_id in page_ids or [] if str(page_id).isdigit()]
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(
        f"""
        SELECT pages.*, pending.snapshot AS draft_snapshot
        FROM pages
        LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
        WHERE pages.project_id = ? AND pages.id IN ({placeholders})
        ORDER BY pages.updated_at DESC
        """,
        (project_id, *ids),
    ).fetchall()
    return [row_to_page(row, portal_type) for row in rows]


def deploy_content_check(project_id, page_ids=None):
    default_portal_type = "department"
    result = {
        "ok": True,
        "projectId": project_id,
        "pageIds": [],
        "errors": [],
        "warnings": [],
        "eligiblePageIds": [],
        "moduleCoverage": module_coverage_from_pages([], default_portal_type),
        "eligibleModuleCoverage": module_coverage_from_pages([], default_portal_type),
    }
    with db_connect() as conn:
        project = conn.execute("SELECT id, config_status, portal_type FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            result["ok"] = False
            result["errors"].append("项目不存在")
            return result
        portal_type = normalize_portal_type(project["portal_type"] if "portal_type" in project.keys() else default_portal_type)
        result["moduleCoverage"] = module_coverage_from_pages([], portal_type)
        result["eligibleModuleCoverage"] = module_coverage_from_pages([], portal_type)
        if project["config_status"] == "pending":
            result["warnings"].append("项目配置有待审核版本")

        eligible_rows = conn.execute(
            "SELECT id FROM pages WHERE project_id = ? AND review_status = 'approved' AND enabled = 1 ORDER BY id",
            (project_id,),
        ).fetchall()
        eligible_ids = [int(row["id"]) for row in eligible_rows]
        result["eligiblePageIds"] = eligible_ids
        result["eligibleModuleCoverage"] = module_coverage_from_pages(
            pages_by_ids_for_coverage(conn, project_id, eligible_ids, portal_type),
            portal_type,
        )

        pending_count = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM pages
            WHERE project_id = ? AND review_status IN ('pending','pending_delete')
            """,
            (project_id,),
        ).fetchone()["value"]
        if int(pending_count or 0):
            result["warnings"].append(f"{int(pending_count)} 个页面仍在等待审核")

        if page_ids is None:
            selected_ids = eligible_ids
        else:
            selected_ids = [int(page_id) for page_id in page_ids if str(page_id).isdigit()]
        result["pageIds"] = selected_ids
        result["moduleCoverage"] = module_coverage_from_pages(
            pages_by_ids_for_coverage(conn, project_id, selected_ids, portal_type),
            portal_type,
        )
        if not selected_ids:
            result["errors"].append("未选择可部署页面")
        missing_modules = result["moduleCoverage"].get("missingLabels", [])
        if selected_ids and missing_modules:
            result["warnings"].append("标准板块未覆盖：" + "、".join(missing_modules))
        for page_id in selected_ids:
            row = conn.execute(
                """
                SELECT id, code, title, body, image_url, enabled, review_status
                FROM pages
                WHERE id = ? AND project_id = ?
                """,
                (page_id, project_id),
            ).fetchone()
            if not row:
                result["errors"].append(f"page {page_id} 不属于当前项目")
                continue
            if row["review_status"] != "approved" or not bool(row["enabled"]):
                result["errors"].append(f"page {row['code']} 未通过审核或未启用")
                continue
            page = {"body": row["body"], "imageUrl": row["image_url"]}
            for url in sorted(page_asset_urls(page)):
                if local_upload_missing(url):
                    result["errors"].append(f"page {row['code']} 缺少资源：{url}")
    result["ok"] = not result["errors"]
    return result


def deploy_content_project(project_id, page_ids=None):
    check = deploy_content_check(project_id, page_ids)
    if not check["ok"]:
        raise ValueError("; ".join(check["errors"]))
    with db_connect() as conn:
        exists = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not exists:
            return None
        if page_ids is None:
            rows = conn.execute(
                "SELECT id FROM pages WHERE project_id = ? AND review_status = 'approved' AND enabled = 1",
                (project_id,),
            ).fetchall()
            page_ids = [row["id"] for row in rows]
        page_ids = [int(page_id) for page_id in page_ids if str(page_id).isdigit()]
        conn.execute("UPDATE projects SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (project_id,))
        conn.execute("DELETE FROM deployed_pages")
        for page_id in page_ids:
            row = conn.execute(
                """
                SELECT id FROM pages
                WHERE id = ? AND project_id = ? AND review_status = 'approved' AND enabled = 1
                """,
                (page_id, project_id),
            ).fetchone()
            if row:
                conn.execute(
                    "INSERT OR IGNORE INTO deployed_pages (project_id, page_id, updated_at) VALUES (?, ?, ?)",
                    (project_id, page_id, now_iso()),
                )
    return get_project(project_id)


def delete_project(project_id):
    with db_connect() as conn:
        row = conn.execute("SELECT id, deployed, content_deployed FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM deployed_pages WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM page_versions WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM project_versions WHERE project_id = ?", (project_id,))
        if table_exists(conn, "content_items"):
            conn.execute(
                """
                DELETE FROM content_item_assets
                WHERE content_item_id IN (SELECT id FROM content_items WHERE project_id = ?)
                """,
                (project_id,),
            )
            conn.execute("DELETE FROM content_item_versions WHERE project_id = ?", (project_id,))
            conn.execute("DELETE FROM content_items WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM pages WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))

        if int(row["deployed"]) == 1 and not conn.execute("SELECT id FROM projects WHERE deployed = 1 LIMIT 1").fetchone():
            fallback = conn.execute(
                "SELECT id FROM projects WHERE portal_type = 'school' ORDER BY updated_at DESC, id DESC LIMIT 1"
            ).fetchone()
            if fallback:
                conn.execute("UPDATE projects SET deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (fallback["id"],))

        if int(row["content_deployed"]) == 1 and not conn.execute(
            "SELECT id FROM projects WHERE content_deployed = 1 LIMIT 1"
        ).fetchone():
            fallback = conn.execute("SELECT id FROM projects ORDER BY updated_at DESC, id DESC LIMIT 1").fetchone()
            if fallback:
                conn.execute(
                    "UPDATE projects SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END",
                    (fallback["id"],),
                )
    return True


def delete_page(project_id, code):
    with db_connect() as conn:
        cursor = conn.execute("DELETE FROM pages WHERE project_id = ? AND code = ?", (project_id, code))
        return cursor.rowcount > 0


def copy_project(project_id, data=None):
    source = get_project(project_id)
    if not source:
        return None

    data = data if isinstance(data, dict) else {}
    name = str(data.get("name") or "").strip() or f"{source['name']} 复制"
    copied = upsert_project(
        None,
        {
            "name": name,
            "portalType": source.get("portalType", "department"),
            "portalSlug": source.get("portalSlug", ""),
            "idleKicker": source.get("idleKicker", ""),
            "idleTitle": source.get("idleTitle", ""),
            "idleCopy": source.get("idleCopy", ""),
            "welcomeKicker": source.get("welcomeKicker", "Welcome"),
            "welcomeTitle": source.get("welcomeTitle", "欢迎参观 {title}"),
            "welcomeSubtitle": source.get("welcomeSubtitle", "即将进入展示页面"),
            "defaultImageUrl": source.get("defaultImageUrl", "/static/expo-stage.png"),
            "accent": source.get("accent", "#f59a13"),
            "displayConfig": source.get("displayConfig", {}),
        },
    )
    if not copied:
        return None

    with db_connect() as conn:
        rows = conn.execute(
            "SELECT * FROM pages WHERE project_id = ? ORDER BY updated_at DESC, id DESC",
            (project_id,),
        ).fetchall()
        for row in rows:
            code = unique_page_code(conn, row["code"])
            conn.execute(
                """
                INSERT INTO pages (
                    project_id, code, category, source, published_at,
                    title, subtitle, body, image_url, content_type, accent, enabled, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    copied["id"],
                    code,
                    row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY,
                    row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
                    row["published_at"] if "published_at" in row.keys() else "",
                    row["title"],
                    row["subtitle"],
                    row["body"],
                    row["image_url"],
                    row["content_type"] if "content_type" in row.keys() else "article",
                    row["accent"],
                    row["enabled"],
                    now_iso(),
                ),
            )

    return copied


def row_to_page(row, portal_type=None):
    if not row:
        return None
    if portal_type is None and "project_portal_type" in row.keys():
        portal_type = row["project_portal_type"]
    portal_type = normalize_portal_type(portal_type or "department")
    category = row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY
    module_key = module_key_for_category(category, portal_type)
    module_meta = module_meta_for_key(module_key, portal_type)
    content_type = normalize_content_type(
        row["content_type"] if "content_type" in row.keys() else default_content_type_for_module(module_key)
    )
    page = {
        "id": row["id"],
        "projectId": row["project_id"],
        "code": row["code"],
        "category": category,
        "moduleKey": module_key,
        "moduleLabel": module_meta["label"] if module_meta else "",
        "contentType": content_type,
        "contentTypeLabel": content_type_label(content_type),
        "source": row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
        "publishedAt": row["published_at"] if "published_at" in row.keys() else "",
        "title": row["title"],
        "subtitle": row["subtitle"],
        "body": row["body"],
        "imageUrl": row["image_url"],
        "accent": row["accent"],
        "enabled": bool(row["enabled"]),
        "reviewStatus": row["review_status"] if "review_status" in row.keys() else "approved",
        "pendingVersionId": row["pending_version_id"] if "pending_version_id" in row.keys() else None,
        "submittedBy": row["submitted_by"] if "submitted_by" in row.keys() else "",
        "reviewedBy": row["reviewed_by"] if "reviewed_by" in row.keys() else "",
        "reviewNote": row["review_note"] if "review_note" in row.keys() else "",
        "qrAvailable": bool(row["enabled"]) and (row["review_status"] if "review_status" in row.keys() else "approved") == "approved",
        "updatedAt": row["updated_at"],
    }
    draft = None
    if "draft_snapshot" in row.keys() and row["draft_snapshot"]:
        try:
            draft = json.loads(row["draft_snapshot"])
        except json.JSONDecodeError:
            draft = None
    if draft:
        page["draft"] = draft
        if page["reviewStatus"] in {"pending", "pending_delete", "rejected"}:
            for key in ("code", "category", "source", "publishedAt", "title", "subtitle", "body", "imageUrl", "contentType", "accent", "enabled"):
                if key in draft:
                    page[key] = draft[key]
            page["deleteRequested"] = page["reviewStatus"] == "pending_delete"
    module_key = module_key_for_category(page.get("category", ""), portal_type)
    module_meta = module_meta_for_key(module_key, portal_type)
    page["moduleKey"] = module_key
    page["moduleLabel"] = module_meta["label"] if module_meta else ""
    page["contentType"] = normalize_content_type(page.get("contentType") or default_content_type_for_module(module_key))
    page["contentTypeLabel"] = content_type_label(page["contentType"])
    page["published"] = {
        "code": row["code"],
        "category": row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY,
        "source": row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
        "publishedAt": row["published_at"] if "published_at" in row.keys() else "",
        "title": row["title"],
        "subtitle": row["subtitle"],
        "body": row["body"],
        "imageUrl": row["image_url"],
        "contentType": normalize_content_type(row["content_type"] if "content_type" in row.keys() else default_content_type_for_module(module_key)),
        "accent": row["accent"],
        "enabled": bool(row["enabled"]),
    }
    return page


def get_page(project_id, code):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot, projects.portal_type AS project_portal_type
            FROM pages
            JOIN projects ON projects.id = pages.project_id
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.project_id = ? AND pages.code = ?
            """,
            (project_id, code),
        ).fetchone()
    return row_to_page(row)


def get_page_by_id(page_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot, projects.portal_type AS project_portal_type
            FROM pages
            JOIN projects ON projects.id = pages.project_id
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.id = ?
            """,
            (page_id,),
        ).fetchone()
    return row_to_page(row)


def get_page_by_code(code):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot
            FROM pages
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.code = ? ORDER BY pages.project_id, pages.id LIMIT 1
            """,
            (code,),
        ).fetchone()
    return row_to_page(row)


def page_code_conflict(project_id, code, exclude_page_id=None):
    with db_connect() as conn:
        if exclude_page_id:
            row = conn.execute(
                "SELECT id, project_id, title FROM pages WHERE project_id = ? AND code = ? AND id != ? LIMIT 1",
                (project_id, code, exclude_page_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, project_id, title FROM pages WHERE project_id = ? AND code = ? LIMIT 1",
                (project_id, code),
            ).fetchone()
    return dict(row) if row else None


def list_pages(project_id):
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot, projects.portal_type AS project_portal_type
            FROM pages
            JOIN projects ON projects.id = pages.project_id
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.project_id = ?
            ORDER BY pages.updated_at DESC
            """,
            (project_id,),
        ).fetchall()
    return [row_to_page(row) for row in rows]


def upsert_page(project_id, code, data):
    code = str(code or "").strip()
    if not code:
        raise ValueError("code 不能为空")

    previous_code = str(data.get("previousCode") or data.get("oldCode") or "").strip()
    current = get_page(project_id, code)
    if not current and previous_code and previous_code != code:
        current = get_page(project_id, previous_code)
    current = current or {}
    current_id = current.get("id")
    conflict = page_code_conflict(project_id, code, current_id)
    if conflict:
        raise ValueError(f"编号 {code} 已被其他展示页使用")

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    if "enabled" in data:
        enabled = 1 if data.get("enabled") else 0
    else:
        enabled = 1 if current.get("enabled", True) else 0

    page = {
        "category": field("category", DEFAULT_PAGE_CATEGORY) or DEFAULT_PAGE_CATEGORY,
        "source": field("source", DEFAULT_PAGE_SOURCE) or DEFAULT_PAGE_SOURCE,
        "published_at": field("publishedAt", field("published_at")),
        "title": field("title", "未命名展示页") or "未命名展示页",
        "subtitle": field("subtitle"),
        "body": sanitize_rich_html(field("body")),
        "image_url": field("imageUrl"),
        "content_type": normalize_content_type(data.get("contentType") or current.get("contentType") or "article"),
        "accent": field("accent", "#0f766e") or "#0f766e",
        "enabled": enabled,
        "updated_at": now_iso(),
    }
    with db_connect() as conn:
        if current_id:
            conn.execute(
                """
                UPDATE pages SET
                    code = ?, category = ?, source = ?, published_at = ?,
                    title = ?, subtitle = ?, body = ?, image_url = ?, content_type = ?,
                    accent = ?, enabled = ?, updated_at = ?
                WHERE id = ? AND project_id = ?
                """,
                (
                    code,
                    page["category"],
                    page["source"],
                    page["published_at"],
                    page["title"],
                    page["subtitle"],
                    page["body"],
                    page["image_url"],
                    page["content_type"],
                    page["accent"],
                    page["enabled"],
                    page["updated_at"],
                    current_id,
                    project_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO pages (
                    project_id, code, category, source, published_at,
                    title, subtitle, body, image_url, content_type, accent, enabled, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    code,
                    page["category"],
                    page["source"],
                    page["published_at"],
                    page["title"],
                    page["subtitle"],
                    page["body"],
                    page["image_url"],
                    page["content_type"],
                    page["accent"],
                    page["enabled"],
                    page["updated_at"],
                ),
            )
            current_id = cursor.lastrowid
    return get_page_by_id(current_id)


def page_payload_from_data(data, current=None):
    current = current or {}

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    enabled = data.get("enabled", current.get("enabled", True))
    category = field("category", DEFAULT_PAGE_CATEGORY) or DEFAULT_PAGE_CATEGORY
    module_key = current.get("moduleKey") or module_key_for_category(category)
    return {
        "code": field("code", current.get("code", "")),
        "category": category,
        "source": field("source", DEFAULT_PAGE_SOURCE) or DEFAULT_PAGE_SOURCE,
        "publishedAt": field("publishedAt", current.get("publishedAt", "")),
        "title": field("title", "Untitled page") or "Untitled page",
        "subtitle": field("subtitle"),
        "body": sanitize_rich_html(field("body")),
        "imageUrl": field("imageUrl"),
        "contentType": normalize_content_type(
            data.get("contentType") or current.get("contentType") or default_content_type_for_module(module_key)
        ),
        "accent": field("accent", "#0f766e") or "#0f766e",
        "enabled": bool(enabled),
    }


def write_page_snapshot(conn, project_id, code, snapshot, current_id=None, actor=None, status="approved", operation="upsert"):
    actor = actor or {"username": ADMIN_USERNAME}
    changes = summarize_changes(page_snapshot_from_row(conn.execute("SELECT * FROM pages WHERE id = ?", (current_id,)).fetchone()) if current_id else {}, snapshot)
    cursor = conn.execute(
        """
        INSERT INTO page_versions (
            page_id, project_id, code, operation, status, snapshot,
            submitted_by, submitted_at, reviewed_by, reviewed_at, changes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            current_id,
            project_id,
            code,
            operation,
            status,
            json.dumps(snapshot, ensure_ascii=False),
            actor.get("username", ADMIN_USERNAME),
            now_iso(),
            actor.get("username", ADMIN_USERNAME) if status == "approved" else "",
            now_iso() if status == "approved" else "",
            changes,
        ),
    )
    return cursor.lastrowid


def apply_page_snapshot(conn, project_id, page_id, snapshot, actor=None):
    actor = actor or {"username": ADMIN_USERNAME}
    now = now_iso()
    if page_id:
        conn.execute(
            """
            UPDATE pages SET
                code = ?, category = ?, source = ?, published_at = ?,
                title = ?, subtitle = ?, body = ?, image_url = ?, content_type = ?, accent = ?,
                enabled = ?, review_status = 'approved', pending_version_id = NULL,
                reviewed_by = ?, review_note = '', updated_at = ?
            WHERE id = ? AND project_id = ?
            """,
            (
                snapshot["code"],
                snapshot["category"],
                snapshot["source"],
                snapshot["publishedAt"],
                snapshot["title"],
                snapshot["subtitle"],
                snapshot["body"],
                snapshot["imageUrl"],
                snapshot["contentType"],
                snapshot["accent"],
                1 if snapshot.get("enabled", True) else 0,
                actor.get("username", ADMIN_USERNAME),
                now,
                page_id,
                project_id,
            ),
        )
        return page_id
    cursor = conn.execute(
        """
        INSERT INTO pages (
            project_id, code, category, source, published_at, title, subtitle,
            body, image_url, content_type, accent, enabled, review_status, submitted_by,
            reviewed_by, review_note, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?, ?, '', ?)
        """,
        (
            project_id,
            snapshot["code"],
            snapshot["category"],
            snapshot["source"],
            snapshot["publishedAt"],
            snapshot["title"],
            snapshot["subtitle"],
            snapshot["body"],
            snapshot["imageUrl"],
            snapshot["contentType"],
            snapshot["accent"],
            1 if snapshot.get("enabled", True) else 0,
            actor.get("username", ADMIN_USERNAME),
            actor.get("username", ADMIN_USERNAME),
            now,
        ),
    )
    return cursor.lastrowid


def save_page(project_id, code, data, actor, approve_now=False):
    code = str(code or "").strip()
    if not code:
        raise ValueError("code 不能为空")
    previous_code = str(data.get("previousCode") or data.get("oldCode") or "").strip()
    current = get_page(project_id, code)
    if not current and previous_code and previous_code != code:
        current = get_page(project_id, previous_code)
    current = current or {}
    current_id = current.get("id")
    conflict = page_code_conflict(project_id, code, current_id)
    if conflict:
        raise ValueError(f"code {code} 已被当前项目中的其他展示页使用")
    snapshot = page_payload_from_data({**data, "code": code}, current)
    with db_connect() as conn:
        if approve_now:
            page_id = apply_page_snapshot(conn, project_id, current_id, snapshot, actor)
            version_id = write_page_snapshot(conn, project_id, snapshot["code"], snapshot, page_id, actor, "approved", "upsert")
            conn.execute("UPDATE page_versions SET page_id = ? WHERE id = ?", (page_id, version_id))
        else:
            if current_id:
                page_id = current_id
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO pages (
                        project_id, code, category, source, published_at, title, subtitle,
                        body, image_url, content_type, accent, enabled, review_status, submitted_by,
                        reviewed_by, review_note, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'pending', ?, '', '', ?)
                    """,
                    (
                        project_id,
                        snapshot["code"],
                        snapshot["category"],
                        snapshot["source"],
                        snapshot["publishedAt"],
                        snapshot["title"],
                        snapshot["subtitle"],
                        snapshot["body"],
                        snapshot["imageUrl"],
                        snapshot["contentType"],
                        snapshot["accent"],
                        actor.get("username", ""),
                        now_iso(),
                    ),
                )
                page_id = cursor.lastrowid
            version_id = write_page_snapshot(conn, project_id, snapshot["code"], snapshot, page_id, actor, "pending", "upsert")
            conn.execute(
                """
                UPDATE pages SET review_status = 'pending', pending_version_id = ?,
                    submitted_by = ?, review_note = '', updated_at = ?
                WHERE id = ?
                """,
                (version_id, actor.get("username", ""), now_iso(), page_id),
            )
    return get_page(project_id, snapshot["code"])


def request_delete_page(project_id, code, actor, approve_now=False):
    page = get_page(project_id, code)
    if not page:
        return False
    snapshot = page.get("published", page)
    with db_connect() as conn:
        if approve_now:
            conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (page["id"],))
            conn.execute(
                "UPDATE pages SET enabled = 0, review_status = 'deleted', pending_version_id = NULL, updated_at = ? WHERE id = ?",
                (now_iso(), page["id"]),
            )
            write_page_snapshot(conn, project_id, code, snapshot, page["id"], actor, "approved", "delete")
        else:
            version_id = write_page_snapshot(conn, project_id, code, snapshot, page["id"], actor, "pending", "delete")
            conn.execute(
                """
                UPDATE pages SET review_status = 'pending_delete', pending_version_id = ?,
                    submitted_by = ?, review_note = '', updated_at = ?
                WHERE id = ?
                """,
                (version_id, actor.get("username", ""), now_iso(), page["id"]),
            )
    return True


def row_to_page_version(row):
    if not row:
        return None
    try:
        snapshot = json.loads(row["snapshot"] or "{}")
    except json.JSONDecodeError:
        snapshot = {}
    current_page = get_page_by_id(row["page_id"]) if row["page_id"] else None
    current = page_public_payload(current_page.get("published") if current_page else None) if current_page else {}
    return {
        "id": row["id"],
        "pageId": row["page_id"],
        "projectId": row["project_id"],
        "projectName": row["project_name"] if "project_name" in row.keys() else "",
        "code": row["code"],
        "operation": row["operation"],
        "status": row["status"],
        "snapshot": snapshot,
        "current": current,
        "diffs": review_diffs(current, snapshot),
        "previewUrl": f"/display?project={row['project_id']}&code={snapshot.get('code') or row['code']}&preview=review&reviewVersion={row['id']}",
        "submittedBy": row["submitted_by"],
        "submittedAt": row["submitted_at"],
        "reviewedBy": row["reviewed_by"],
        "reviewedAt": row["reviewed_at"],
        "reviewNote": row["review_note"],
        "changes": row["changes"],
    }


def row_to_project_version(row):
    if not row:
        return None
    try:
        snapshot = json.loads(row["snapshot"] or "{}")
    except json.JSONDecodeError:
        snapshot = {}
    current_project = get_project(row["project_id"])
    current = project_public_payload(current_project) if current_project else {}
    return {
        "id": row["id"],
        "projectId": row["project_id"],
        "projectName": row["project_name"] if "project_name" in row.keys() else "",
        "status": row["status"],
        "snapshot": snapshot,
        "current": current,
        "diffs": review_diffs(current, snapshot),
        "submittedBy": row["submitted_by"],
        "submittedAt": row["submitted_at"],
        "reviewedBy": row["reviewed_by"],
        "reviewedAt": row["reviewed_at"],
        "reviewNote": row["review_note"],
        "changes": row["changes"],
    }


def list_reviews(status="pending"):
    with db_connect() as conn:
        page_rows = conn.execute(
            """
            SELECT page_versions.*, projects.name AS project_name
            FROM page_versions
            JOIN projects ON projects.id = page_versions.project_id
            WHERE page_versions.status = ?
            ORDER BY page_versions.submitted_at DESC, page_versions.id DESC
            """,
            (status,),
        ).fetchall()
        project_rows = conn.execute(
            """
            SELECT project_versions.*, projects.name AS project_name
            FROM project_versions
            JOIN projects ON projects.id = project_versions.project_id
            WHERE project_versions.status = ?
            ORDER BY project_versions.submitted_at DESC, project_versions.id DESC
            """,
            (status,),
        ).fetchall()
        content_item_rows = conn.execute(
            """
            SELECT content_item_versions.*, projects.name AS project_name
            FROM content_item_versions
            JOIN projects ON projects.id = content_item_versions.project_id
            WHERE content_item_versions.status = ?
            ORDER BY content_item_versions.submitted_at DESC, content_item_versions.id DESC
            """,
            (status,),
        ).fetchall()
    return {
        "pages": [row_to_page_version(row) for row in page_rows],
        "projects": [row_to_project_version(row) for row in project_rows],
        "contentItems": [row_to_content_item_version(row) for row in content_item_rows],
    }


def list_project_versions(project_id):
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT project_versions.*, projects.name AS project_name
            FROM project_versions
            JOIN projects ON projects.id = project_versions.project_id
            WHERE project_versions.project_id = ?
            ORDER BY project_versions.submitted_at DESC, project_versions.id DESC
            """,
            (project_id,),
        ).fetchall()
    return [row_to_project_version(row) for row in rows]


def list_page_versions(project_id, code):
    page = get_page(project_id, code)
    page_id = page["id"] if page else 0
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT page_versions.*, projects.name AS project_name
            FROM page_versions
            JOIN projects ON projects.id = page_versions.project_id
            WHERE page_versions.project_id = ?
              AND (page_versions.page_id = ? OR page_versions.code = ?)
            ORDER BY page_versions.submitted_at DESC, page_versions.id DESC
            """,
            (project_id, page_id, code),
        ).fetchall()
    return [row_to_page_version(row) for row in rows]


def approve_page_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM page_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        version = row_to_page_version(row)
        snapshot = version["snapshot"]
        if version["operation"] == "delete":
            conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (version["pageId"],))
            conn.execute(
                """
                UPDATE pages SET enabled = 0, review_status = 'deleted', pending_version_id = NULL,
                    reviewed_by = ?, review_note = ?, updated_at = ?
                WHERE id = ?
                """,
                (actor["username"], note, now_iso(), version["pageId"]),
            )
        else:
            page_id = apply_page_snapshot(conn, version["projectId"], version["pageId"], snapshot, actor)
            conn.execute("UPDATE page_versions SET page_id = ? WHERE id = ?", (page_id, version_id))
        conn.execute(
            """
            UPDATE page_versions SET status = 'approved', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
    return get_page_by_id(version["pageId"]) if version["pageId"] else None


def reject_page_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM page_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        conn.execute(
            """
            UPDATE page_versions SET status = 'rejected', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
        conn.execute(
            """
            UPDATE pages SET review_status = 'rejected', review_note = ?,
                reviewed_by = ?, updated_at = ?
            WHERE pending_version_id = ?
            """,
            (note, actor["username"], now_iso(), version_id),
        )
    return row_to_page_version(row)


def approve_project_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM project_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        version = row_to_project_version(row)
        snapshot = version["snapshot"]
        payload = project_payload_from_data(snapshot, get_project(version["projectId"]))
        conn.execute(
            """
            UPDATE projects SET
                name = ?, portal_type = ?, portal_slug = ?, idle_kicker = ?, idle_title = ?, idle_copy = ?,
                welcome_kicker = ?, welcome_title = ?, welcome_subtitle = ?,
                default_image_url = ?, accent = ?, display_config = ?,
                config_status = 'approved', pending_config_version_id = NULL, updated_at = ?
            WHERE id = ?
            """,
            (
                payload["name"],
                payload["portal_type"],
                payload["portal_slug"],
                payload["idle_kicker"],
                payload["idle_title"],
                payload["idle_copy"],
                payload["welcome_kicker"],
                payload["welcome_title"],
                payload["welcome_subtitle"],
                payload["default_image_url"],
                payload["accent"],
                payload["display_config"],
                now_iso(),
                version["projectId"],
            ),
        )
        conn.execute(
            """
            UPDATE project_versions SET status = 'approved', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
    return get_project(version["projectId"])


def reject_project_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM project_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        version = row_to_project_version(row)
        conn.execute(
            """
            UPDATE project_versions SET status = 'rejected', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
        conn.execute(
            """
            UPDATE projects SET config_status = 'rejected', updated_at = ?
            WHERE pending_config_version_id = ?
            """,
            (now_iso(), version_id),
        )
    return version


def get_display_project(project_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.id = ? AND COALESCE(users.enabled, 1) = 1
            """,
            (project_id,),
        ).fetchone()
    return row_to_project(row)


def get_display_page(project_id, code, require_deployed=False):
    with db_connect() as conn:
        sql = """
            SELECT pages.*, NULL AS draft_snapshot, projects.portal_type AS project_portal_type
            FROM pages
            JOIN projects ON projects.id = pages.project_id
            LEFT JOIN users ON users.username = projects.owner_username
        """
        params = [project_id, code]
        where = """
            WHERE pages.project_id = ?
              AND pages.code = ?
              AND pages.review_status = 'approved'
              AND pages.enabled = 1
              AND COALESCE(users.enabled, 1) = 1
        """
        if require_deployed:
            sql += " JOIN deployed_pages ON deployed_pages.page_id = pages.id AND deployed_pages.project_id = pages.project_id "
            where += " AND projects.content_deployed = 1"
        row = conn.execute(sql + where, params).fetchone()
    return row_to_page(row)


def get_public_portal_content(portal_type, portal_slug):
    portal_type = normalize_portal_type(portal_type)
    portal_slug = normalize_portal_slug(portal_slug)
    if portal_type not in {"department", "topic"} or not portal_slug:
        return None
    with db_connect() as conn:
        project_row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.portal_type = ?
              AND p.portal_slug = ?
              AND p.config_status = 'approved'
              AND COALESCE(users.enabled, 1) = 1
            ORDER BY p.content_deployed DESC, p.updated_at DESC, p.id DESC
            LIMIT 1
            """,
            (portal_type, portal_slug),
        ).fetchone()
        if not project_row:
            return None
        page_rows = conn.execute(
            """
            SELECT pages.*, NULL AS draft_snapshot, projects.portal_type AS project_portal_type
            FROM pages
            JOIN projects ON projects.id = pages.project_id
            WHERE pages.project_id = ?
              AND pages.review_status = 'approved'
              AND pages.enabled = 1
            ORDER BY pages.updated_at DESC, pages.id DESC
            """,
            (project_row["id"],),
        ).fetchall()
    pages = [row_to_page(row, portal_type) for row in page_rows]
    content_items = [
        item for item in list_content_items(project_row["id"], {"reviewStatus": "approved", "enabled": "1"})
        if item.get("enabled") and item.get("reviewStatus") == "approved"
    ]
    project = row_to_project(project_row)
    project["pageCount"] = len(pages)
    project["pendingPageCount"] = 0
    return {
        "project": project,
        "pages": pages,
        "contentItems": content_items,
        "modules": content_modules_payload(content_items, portal_type),
        "coverage": module_coverage_from_pages(pages, portal_type),
    }


def scan_code_candidates(code):
    text = str(code or "").strip()
    if not text:
        return []
    candidates = [text]
    if re.fullmatch(r"\d{5,}", text):
        candidates.append(f"DEMO-{text}")
    if text.upper().startswith("DEMO-") and len(text) > 5:
        candidates.append(text[5:])
    unique = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def find_deployed_display_page(project_id, code):
    for candidate in scan_code_candidates(code):
        page = get_display_page(project_id, candidate, require_deployed=True)
        if page:
            return candidate, page
    return str(code or "").strip(), None


def validated_latest_scan():
    global LAST_SCAN
    scan = LAST_SCAN
    if not scan:
        return None
    try:
        received_at = datetime.fromisoformat(str(scan.get("receivedAt", "")).replace("Z", "+00:00"))
        if (datetime.now(timezone.utc) - received_at).total_seconds() > LATEST_SCAN_SECONDS:
            LAST_SCAN = None
            return None
    except Exception:
        LAST_SCAN = None
        return None
    if scan.get("external"):
        return scan
    project = get_deployed_content_project()
    code = str(scan.get("code") or "")
    project_id = (scan.get("project") or {}).get("id")
    if not project or (project_id and int(project_id) != int(project["id"])):
        LAST_SCAN = None
        return None
    matched_code, page = find_deployed_display_page(project["id"], code)
    if not page:
        LAST_SCAN = None
        return None
    code = matched_code
    scan["code"] = code
    scan["project"] = project
    scan["page"] = page
    scan["localDisplayUrl"] = f"/display?project={project['id']}&code={code}"
    scan["displayUrl"] = scan["localDisplayUrl"]
    return scan


def deployed_page_ids(project_id):
    with db_connect() as conn:
        rows = conn.execute("SELECT page_id FROM deployed_pages WHERE project_id = ?", (project_id,)).fetchall()
    return [row["page_id"] for row in rows]


def extract_code(value):
    text = str(value or "").strip()
    if not text:
        return ""

    parsed = urlparse(text)
    haystack = " ".join([parsed.path, parsed.params, parsed.query, parsed.fragment, text])

    match = re.search(r"activePage/([A-Za-z0-9_-]+)", haystack)
    if match:
        return match.group(1)

    numeric = re.findall(r"\d{5,}", haystack)
    if numeric:
        return numeric[-1]

    return text[-64:]


def normalize_scan_url(value):
    text = str(value or "").strip()
    markdown_match = re.search(r"\((https?://[^)\s]+)\)", text)
    if markdown_match:
        text = markdown_match.group(1)

    inline_match = re.search(r"https?://[^\s\"'<>]+", text)
    if inline_match:
        text = inline_match.group(0)

    parsed = urlparse(text)
    if parsed.scheme not in ("http", "https"):
        return None
    return text


def extract_scan_target(value):
    text = unquote(str(value or "").strip())
    parsed = urlparse(text)
    query = parse_qs(parsed.query)
    if parsed.fragment:
        fragment = parsed.fragment
        if "?" in fragment:
            fragment = fragment.split("?", 1)[1]
        fragment_query = parse_qs(fragment)
        for key, values in fragment_query.items():
            query.setdefault(key, values)

    def first_value(*names):
        for name in names:
            values = query.get(name)
            if values and str(values[0]).strip():
                return str(values[0]).strip()
        return ""

    project_text = first_value("project", "projectId", "pid")
    code = first_value("code", "page", "pageCode")
    project_id = int(project_text) if project_text.isdigit() else None
    if code:
        return project_id, code[-64:]

    haystack = " ".join([parsed.path, parsed.params, parsed.query, parsed.fragment, text])
    match = re.search(r"activePage/([A-Za-z0-9_-]+)", haystack)
    if match:
        return project_id, match.group(1)

    numeric = re.findall(r"\d{5,}", haystack)
    if numeric:
        return project_id, numeric[-1]

    return project_id, text[-64:] if text else ""


def is_admin_display_url(value):
    parsed = urlparse(str(value or "").strip())
    host = parsed.netloc.lower()
    query = parse_qs(parsed.query)
    source = (query.get("source") or [""])[0]
    path = parsed.path.rstrip("/") or "/"
    local_hosts = {"", "127.0.0.1", "localhost", f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
    return (
        source == "expo-admin"
        or (path == "/display" and (not host or host in local_hosts))
    )


def is_external_url(value):
    parsed = urlparse(str(value or "").strip())
    if parsed.scheme not in ("http", "https"):
        return False
    return not is_admin_display_url(value)


def init_qr_field():
    value = 1
    for i in range(255):
        GF_EXP[i] = value
        GF_LOG[value] = i
        value <<= 1
        if value & 0x100:
            value ^= 0x11D
    for i in range(255, 512):
        GF_EXP[i] = GF_EXP[i - 255]


def qr_mul(left, right):
    if not left or not right:
        return 0
    return GF_EXP[GF_LOG[left] + GF_LOG[right]]


def qr_generator_poly(degree):
    poly = [1]
    for i in range(degree):
        next_poly = [0] * (len(poly) + 1)
        for j, coefficient in enumerate(poly):
            next_poly[j] ^= coefficient
            next_poly[j + 1] ^= qr_mul(coefficient, GF_EXP[i])
        poly = next_poly
    return poly


def qr_rs_remainder(data, degree):
    generator = qr_generator_poly(degree)
    result = [0] * degree
    for byte in data:
        factor = byte ^ result.pop(0)
        result.append(0)
        for i in range(degree):
            result[i] ^= qr_mul(generator[i + 1], factor)
    return result


def append_bits(target, value, length):
    for i in range(length - 1, -1, -1):
        target.append((value >> i) & 1)


def qr_format_bits(mask):
    data = (0b01 << 3) | mask
    value = data << 10
    generator = 0x537
    for i in range(14, 9, -1):
        if (value >> i) & 1:
            value ^= generator << (i - 10)
    return ((data << 10) | value) ^ 0x5412


def make_qr_matrix(text):
    if not GF_EXP[0]:
        init_qr_field()

    payload = str(text or "").encode("utf-8")
    if not payload:
        raise ValueError("二维码内容不能为空")

    version = None
    data_codewords = ecc_codewords = 0
    bit_length = 4 + 8 + len(payload) * 8
    for candidate, (data_count, ecc_count) in QR_L_CAPACITY.items():
        if bit_length <= data_count * 8:
            version = candidate
            data_codewords = data_count
            ecc_codewords = ecc_count
            break
    if version is None:
        raise ValueError("二维码内容太长")

    bits = []
    append_bits(bits, 0b0100, 4)
    append_bits(bits, len(payload), 8)
    for byte in payload:
        append_bits(bits, byte, 8)

    capacity_bits = data_codewords * 8
    append_bits(bits, 0, min(4, capacity_bits - len(bits)))
    while len(bits) % 8:
        bits.append(0)

    data = []
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i : i + 8]:
            byte = (byte << 1) | bit
        data.append(byte)

    pad = 0xEC
    while len(data) < data_codewords:
        data.append(pad)
        pad ^= 0xEC ^ 0x11

    codewords = data + qr_rs_remainder(data, ecc_codewords)
    stream = []
    for byte in codewords:
        append_bits(stream, byte, 8)

    size = version * 4 + 17
    modules = [[False for _ in range(size)] for _ in range(size)]
    reserved = [[False for _ in range(size)] for _ in range(size)]

    def set_module(row, col, dark, reserve=True):
        if 0 <= row < size and 0 <= col < size:
            modules[row][col] = bool(dark)
            if reserve:
                reserved[row][col] = True

    def draw_finder(row, col):
        for dy in range(-1, 8):
            for dx in range(-1, 8):
                rr = row + dy
                cc = col + dx
                dark = (
                    0 <= dx <= 6
                    and 0 <= dy <= 6
                    and (dx in (0, 6) or dy in (0, 6) or (2 <= dx <= 4 and 2 <= dy <= 4))
                )
                set_module(rr, cc, dark)

    draw_finder(0, 0)
    draw_finder(0, size - 7)
    draw_finder(size - 7, 0)

    for i in range(8, size - 8):
        dark = i % 2 == 0
        set_module(6, i, dark)
        set_module(i, 6, dark)

    positions = QR_ALIGNMENT[version]
    for row in positions:
        for col in positions:
            if reserved[row][col]:
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    distance = max(abs(dx), abs(dy))
                    set_module(row + dy, col + dx, distance == 2 or distance == 0)

    for i in range(9):
        if i != 6:
            set_module(8, i, False)
            set_module(i, 8, False)
    for i in range(8):
        set_module(8, size - 1 - i, False)
    for i in range(7):
        set_module(size - 1 - i, 8, False)
    set_module(version * 4 + 9, 8, True)

    bit_index = 0
    upward = True
    col = size - 1
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for row in rows:
            for cc in (col, col - 1):
                if reserved[row][cc]:
                    continue
                bit = stream[bit_index] if bit_index < len(stream) else 0
                bit_index += 1
                set_module(row, cc, bool(bit) ^ ((row + cc) % 2 == 0), False)
        upward = not upward
        col -= 2

    fmt = qr_format_bits(0)
    for i in range(15):
        bit = (fmt >> i) & 1
        if i < 6:
            set_module(i, 8, bit)
        elif i < 8:
            set_module(i + 1, 8, bit)
        else:
            set_module(size - 15 + i, 8, bit)

        if i < 8:
            set_module(8, size - i - 1, bit)
        elif i < 9:
            set_module(8, 8 - 1, bit)
        else:
            set_module(8, 15 - i - 1, bit)
    set_module(size - 8, 8, True)
    return modules


def qr_svg(text):
    modules = make_qr_matrix(text)
    border = 4
    size = len(modules) + border * 2
    parts = []
    for row, line in enumerate(modules):
        for col, dark in enumerate(line):
            if dark:
                parts.append(f"M{col + border},{row + border}h1v1h-1z")
    title = xml_escape(str(text or ""))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="512" height="512" role="img" aria-label="QR code">'
        f"<title>{title}</title>"
        f'<rect width="{size}" height="{size}" fill="#fff"/>'
        f'<path d="{" ".join(parts)}" fill="#000"/>'
        "</svg>"
    )


def broadcast_scan(scan):
    payload = f"event: scan\ndata: {json.dumps(scan, ensure_ascii=False)}\n\n".encode("utf-8")
    dead = []
    for client in list(SSE_CLIENTS):
        try:
            client.write(payload)
            client.flush()
        except Exception:
            dead.append(client)
    for client in dead:
        SSE_CLIENTS.discard(client)


def tcp_port_open(host, port, timeout=0.35):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def start_unity_model_server():
    global UNITY_MODEL_PROCESS
    model_dir = UNITY_MODEL_DIR.resolve()
    if not model_dir.exists() or not (model_dir / "index.html").exists():
        return {"ok": False, "error": "Unity 模型目录不存在或缺少 index.html", "url": UNITY_MODEL_URL}

    if tcp_port_open(UNITY_MODEL_HOST, UNITY_MODEL_PORT):
        return {"ok": True, "url": UNITY_MODEL_URL, "alreadyRunning": True}

    with UNITY_MODEL_LOCK:
        if UNITY_MODEL_PROCESS and UNITY_MODEL_PROCESS.poll() is None:
            return {"ok": True, "url": UNITY_MODEL_URL, "alreadyRunning": True}
        if tcp_port_open(UNITY_MODEL_HOST, UNITY_MODEL_PORT):
            return {"ok": True, "url": UNITY_MODEL_URL, "alreadyRunning": True}

        commands = [
            ["py", "-m", "http.server", str(UNITY_MODEL_PORT), "--bind", UNITY_MODEL_HOST],
            [sys.executable, "-m", "http.server", str(UNITY_MODEL_PORT), "--bind", UNITY_MODEL_HOST],
        ]
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        last_error = ""
        for command in commands:
            try:
                UNITY_MODEL_PROCESS = subprocess.Popen(
                    command,
                    cwd=str(model_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags,
                )
                break
            except OSError as exc:
                UNITY_MODEL_PROCESS = None
                last_error = str(exc)

        if not UNITY_MODEL_PROCESS:
            return {"ok": False, "error": f"启动 Unity 模型服务失败：{last_error}", "url": UNITY_MODEL_URL}

        for _ in range(30):
            if tcp_port_open(UNITY_MODEL_HOST, UNITY_MODEL_PORT, timeout=0.15):
                return {"ok": True, "url": UNITY_MODEL_URL, "started": True}
            if UNITY_MODEL_PROCESS.poll() is not None:
                return {"ok": False, "error": "Unity 模型服务启动后立即退出", "url": UNITY_MODEL_URL}
            time.sleep(0.1)

        return {"ok": False, "error": "Unity 模型服务启动超时", "url": UNITY_MODEL_URL}


def content_type_for(path):
    suffix = path.suffix.lower()
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "application/octet-stream")


def is_relative_to(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class ExpoHandler(BaseHTTPRequestHandler):
    server_version = "ExpoDisplay/0.1"

    def handle(self):
        try:
            super().handle()
        except RequestRejected:
            pass
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            pass

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def cors_origin(self):
        origin = self.headers.get("Origin", "").rstrip("/")
        if not origin or not ALLOWED_ORIGINS:
            return ""
        if "*" in ALLOWED_ORIGINS:
            return origin if self.headers.get("Cookie") else "*"
        return origin if origin in ALLOWED_ORIGINS else ""

    def send_cors_headers(self):
        origin = self.cors_origin()
        if not origin:
            return
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        if origin != "*":
            self.send_header("Access-Control-Allow-Credentials", "true")

    def send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: http: https:; "
            "connect-src 'self' http: https:; "
            "font-src 'self' data:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'self'",
        )

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_security_headers()
        self.send_cors_headers()
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def send_redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def read_json(self, max_bytes=MAX_JSON_BYTES):
        length = int(self.headers.get("Content-Length", "0"))
        if length > max_bytes:
            self.send_json(413, {"ok": False, "error": "请求内容太大"})
            raise RequestRejected()
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        if not raw.strip():
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"url": raw.strip()}

    def cookie_value(self, name):
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        if name not in cookie:
            return ""
        return cookie[name].value

    def current_admin(self):
        user = self.current_user()
        return user["username"] if user and user.get("role") == "admin" else None

    def current_user(self):
        return get_session_user(self.cookie_value(ADMIN_COOKIE))

    def require_auth(self):
        user = self.current_user()
        if user:
            return user
        self.send_json(401, {"ok": False, "error": "请先登录"})
        return None

    def require_admin(self):
        user = self.current_user()
        if user and user.get("role") == "admin":
            return user
        self.send_json(401, {"ok": False, "error": "需要管理员权限"})
        return None

    def csrf_exempt(self, path):
        return path in {"/api/login", "/api/scan", "/api/scans"}

    def require_csrf(self, path):
        if self.command not in {"POST", "PUT", "DELETE"} or self.csrf_exempt(path):
            return True
        token = self.cookie_value(ADMIN_COOKIE)
        expected = csrf_token_for_session(token)
        provided = self.headers.get("X-CSRF-Token", "")
        if expected and hmac.compare_digest(provided, expected):
            return True
        self.send_json(403, {"ok": False, "error": "登录状态已失效，请刷新页面后重试"})
        return False

    def admin_username(self):
        user = self.current_user()
        return user["username"] if user else ""

    def user_role(self):
        user = self.current_user()
        return user.get("role", "") if user else ""

    def client_ip(self):
        if TRUST_PROXY_HEADERS:
            forwarded = self.headers.get("X-Forwarded-For", "")
            if forwarded:
                first = forwarded.split(",", 1)[0].strip()
                if first:
                    return first
            real_ip = self.headers.get("X-Real-IP", "").strip()
            if real_ip:
                return real_ip
        return self.client_address[0] if self.client_address else ""

    def log_admin(self, action, target_type="", target_id="", target_label="", detail="", changes=""):
        user = self.current_user() or {}
        create_admin_log(
            action,
            target_type=target_type,
            target_id=target_id,
            target_label=target_label,
            detail=detail,
            username=user.get("username", self.admin_username()),
            role=user.get("role", self.user_role()),
            ip=self.client_ip(),
            changes=changes,
        )

    def session_cookie_header(self, token):
        secure = "; Secure" if SESSION_COOKIE_SECURE else ""
        return (
            f"{ADMIN_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; "
            f"Max-Age={ADMIN_SESSION_SECONDS}{secure}"
        )

    def clear_session_cookie_header(self):
        secure = "; Secure" if SESSION_COOKIE_SECURE else ""
        return f"{ADMIN_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0{secure}"

    def serve_file(self, path):
        try:
            resolved = path.resolve()
            allowed_roots = (STATIC_DIR.resolve(), UPLOAD_DIR.resolve())
            if not any(is_relative_to(resolved, root) for root in allowed_roots):
                self.send_error(403)
                return
            body = resolved.read_bytes()
        except FileNotFoundError:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type_for(resolved))
        if resolved.suffix.lower() in {".html", ".css", ".js"}:
            self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Content-Length", str(len(body)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-CSRF-Token")
        self.send_security_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/display")
            self.end_headers()
            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path == "/display":
            self.serve_file(STATIC_DIR / "display.html")
            return

        # 数字门户展厅（DESIGN.md）：学校门户与二级门户共用入口
        if (
            path == "/departments"
            or path.startswith("/departments/")
            or path == "/topics"
            or path.startswith("/topics/")
        ):
            self.serve_file(STATIC_DIR / "blueprint" / "index.html")
            return

        if path == "/login":
            user = self.current_user()
            if user:
                self.send_redirect("/admin" if user.get("role") == "admin" else "/teacher?view=pages")
                return
            self.serve_file(STATIC_DIR / "login.html")
            return

        if path == "/admin":
            user = self.current_user()
            if not user:
                self.send_redirect("/login")
                return
            if user.get("role") != "admin":
                self.send_redirect("/teacher?view=pages")
                return
            self.serve_file(STATIC_DIR / "admin.html")
            return

        if path == "/teacher":
            user = self.current_user()
            if not user:
                self.send_redirect("/login")
                return
            if user.get("role") == "admin":
                self.send_redirect("/admin")
                return
            self.serve_file(STATIC_DIR / "admin.html")
            return

        if path == "/api/health":
            self.send_json(200, {"ok": True, "clients": len(SSE_CLIENTS), "time": now_iso()})
            return

        if path == "/api/ready":
            status = ready_status()
            self.send_json(200 if status["ok"] else 503, status)
            return

        if path == "/api/unityceshi111/open":
            status = start_unity_model_server()
            if not status["ok"]:
                self.send_json(500, status)
                return
            self.send_response(302)
            self.send_header("Location", status["url"])
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.end_headers()
            return

        if path == "/api/unityceshi111/start":
            status = start_unity_model_server()
            self.send_json(200 if status["ok"] else 500, status)
            return

        if path == "/api/session":
            user = self.current_user()
            permissions = []
            if user:
                permissions = ["admin"] if user["role"] == "admin" else ["teacher"]
            token = self.cookie_value(ADMIN_COOKIE)
            self.send_json(
                200,
                {
                    "ok": True,
                    "authenticated": bool(user),
                    "user": user,
                    "permissions": permissions,
                    "username": user["username"] if user else "",
                    "csrfToken": csrf_token_for_session(token) if user else "",
                },
            )
            return

        if path == "/api/admin/dashboard":
            user = self.require_auth()
            if not user:
                return
            self.send_json(200, {"ok": True, "dashboard": admin_dashboard(user)})
            return

        if path == "/api/admin/logs":
            if not self.require_admin():
                return
            limit = parse_qs(parsed.query).get("limit", ["80"])[0]
            query = parse_qs(parsed.query)
            self.send_json(
                200,
                {
                    "ok": True,
                    "logs": list_admin_logs(
                        limit,
                        username=(query.get("username") or [""])[0],
                        action=(query.get("action") or [""])[0],
                        date_from=(query.get("from") or [""])[0],
                        date_to=(query.get("to") or [""])[0],
                    ),
                },
            )
            return

        if path == "/api/admin/acceptance-report.json":
            user = self.require_admin()
            if not user:
                return
            self.send_json(
                200,
                {"ok": True, "report": acceptance_report(user)},
                {"Content-Disposition": 'attachment; filename="expo-acceptance-report.json"'},
            )
            return

        if path == "/api/admin/logs.csv":
            if not self.require_admin():
                return
            query = parse_qs(parsed.query)
            rows = list_admin_logs(
                300,
                username=(query.get("username") or [""])[0],
                action=(query.get("action") or [""])[0],
                date_from=(query.get("from") or [""])[0],
                date_to=(query.get("to") or [""])[0],
            )
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["createdAt", "username", "role", "action", "targetType", "targetId", "targetLabel", "detail", "changes", "ip"], extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            body = output.getvalue().encode("utf-8-sig")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="admin-logs.csv"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/display/project":
            project = get_deployed_project()
            self.send_json(200, {"ok": True, "project": project})
            return

        if path == "/api/display/latest":
            self.send_json(200, {"ok": True, "scan": validated_latest_scan()})
            return

        if path.startswith("/api/display/projects/"):
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "display" and parts[2] == "projects":
                project_id = int(parts[3]) if parts[3].isdigit() else 0
                project = get_display_project(project_id)
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 6 and parts[0] == "api" and parts[1] == "display" and parts[2] == "projects" and parts[4] == "pages":
                project_id = int(parts[3]) if parts[3].isdigit() else 0
                code = parts[5]
                project = get_display_project(project_id)
                page = get_display_page(project_id, code, require_deployed=False) if project else None
                if not project or not page:
                    self.send_json(404, {"ok": False, "error": "页面不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "page": page})
                return

        if path.startswith("/api/portal/"):
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "portal":
                kind = parts[2]
                portal_type = {"departments": "department", "department": "department", "topics": "topic", "topic": "topic"}.get(kind)
                portal = get_public_portal_content(portal_type, parts[3]) if portal_type else None
                if not portal:
                    self.send_json(404, {"ok": False, "error": "portal not found"})
                    return
                self.send_json(200, {"ok": True, **portal})
                return

        if path == "/api/qr-public":
            # 公开二维码（无需登录），供大屏展示页使用；data 限长防滥用
            data = parse_qs(parsed.query).get("data", [""])[0]
            if len(data) > 512:
                self.send_json(400, {"ok": False, "error": "二维码内容过长"})
                return
            try:
                body = qr_svg(data).encode("utf-8")
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
            self.send_header("Content-Disposition", 'inline; filename="display-qr.svg"')
            self.send_header("Content-Length", str(len(body)))
            self.send_security_headers()
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/qr":
            if not self.require_auth():
                return
            data = parse_qs(parsed.query).get("data", [""])[0]
            try:
                body = qr_svg(data).encode("utf-8")
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
            self.send_header("Content-Disposition", 'inline; filename="display-qr.svg"')
            self.send_header("Content-Length", str(len(body)))
            self.send_security_headers()
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/users":
            if not self.require_admin():
                return
            self.send_json(200, {"ok": True, "users": list_users()})
            return

        if path == "/api/assets":
            user = self.require_auth()
            if not user:
                return
            limit = (parse_qs(parsed.query).get("limit") or ["80"])[0]
            self.send_json(200, {"ok": True, "assets": list_assets(user, limit)})
            return

        if path == "/api/content/templates":
            if not self.require_auth():
                return
            self.send_json(200, {"ok": True, **content_templates_payload()})
            return

        if path == "/api/reviews":
            if not self.require_admin():
                return
            status = (parse_qs(parsed.query).get("status") or ["pending"])[0]
            self.send_json(200, {"ok": True, "reviews": list_reviews(status)})
            return

        if path.startswith("/api/reviews/pages/") and path.endswith("/preview"):
            if not self.require_admin():
                return
            parts = path.strip("/").split("/")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "reviews" and parts[2] == "pages":
                version_id = int(parts[3]) if parts[3].isdigit() else 0
                with db_connect() as conn:
                    row = conn.execute(
                        """
                        SELECT page_versions.*, projects.name AS project_name
                        FROM page_versions
                        JOIN projects ON projects.id = page_versions.project_id
                        WHERE page_versions.id = ?
                        """,
                        (version_id,),
                    ).fetchone()
                version = row_to_page_version(row) if row else None
                project = get_project(version["projectId"]) if version else None
                if not version or not project:
                    self.send_json(404, {"ok": False, "error": "审核记录不存在"})
                    return
                page = {**version["snapshot"], "projectId": version["projectId"], "reviewStatus": version["status"], "qrAvailable": False}
                self.send_json(200, {"ok": True, "project": project, "page": page, "review": version})
                return

        if path.startswith("/api/deploy/content/"):
            if not self.require_admin():
                return
            project_id_text = path.rsplit("/", 1)[-1]
            project_id = int(project_id_text) if project_id_text.isdigit() else 0
            self.send_json(200, {"ok": True, "pageIds": deployed_page_ids(project_id)})
            return

        if path.startswith("/api/deploy/check/"):
            if not self.require_admin():
                return
            project_id_text = path.rsplit("/", 1)[-1]
            project_id = int(project_id_text) if project_id_text.isdigit() else 0
            self.send_json(200, {"ok": True, "check": deploy_content_check(project_id)})
            return

        if path == "/api/projects":
            user = self.require_auth()
            if not user:
                return
            self.send_json(
                200,
                {
                    "ok": True,
                    "projects": list_projects(user),
                    "deployedProjectId": (get_deployed_project() or {}).get("id"),
                    "deployedContentProjectId": (get_deployed_content_project() or {}).get("id"),
                },
            )
            return

        if path == "/api/lowcode/forms":
            user = self.require_auth()
            if not user:
                return
            filters = {key: values[0] for key, values in parse_qs(parsed.query).items() if values}
            if user.get("role") != "admin":
                filters["enabled"] = "1"
            self.send_json(200, {"ok": True, "forms": list_lowcode_forms(filters)})
            return

        if path.startswith("/api/lowcode/forms/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "lowcode" and parts[2] == "forms" and parts[4] == "versions":
                actor = self.require_admin()
                if not actor:
                    return
                form_id = int(parts[3]) if parts[3].isdigit() else 0
                form = get_lowcode_form(form_id)
                if not form:
                    self.send_json(404, {"ok": False, "error": "资料采集模板不存在"})
                    return
                self.send_json(200, {"ok": True, "form": form, "versions": list_lowcode_form_versions(form_id)})
                return
            form_id_text = parts[-1]
            form_id = int(form_id_text) if form_id_text.isdigit() else 0
            form = get_lowcode_form(form_id)
            if not form or (not form.get("enabled") and user.get("role") != "admin"):
                self.send_json(404, {"ok": False, "error": "资料采集模板不存在"})
                return
            self.send_json(200, {"ok": True, "form": form})
            return

        if path.startswith("/api/projects/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "versions":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "versions": list_project_versions(project_id)})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "content-items":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                filters = {key: values[0] for key, values in parse_qs(parsed.query).items() if values}
                self.send_json(
                    200,
                    {
                        "ok": True,
                        "project": project,
                        "items": list_content_items(project_id, filters),
                        "templates": content_templates_payload(),
                    },
                )
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "lowcode" and parts[4] == "forms":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                filters = {
                    "portalType": project.get("portalType"),
                }
                if user.get("role") != "admin":
                    filters["enabled"] = "1"
                self.send_json(200, {"ok": True, "project": project, "forms": list_lowcode_forms(filters)})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "lowcode" and parts[4] == "records":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "records": list_lowcode_records(project_id)})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "content-items":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                content_item_id = int(parts[4]) if parts[4].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                item = get_content_item(project_id, content_item_id)
                if not item:
                    self.send_json(404, {"ok": False, "error": "资料不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "item": item})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                pages = list_pages(project_id)
                self.send_json(
                    200,
                    {"ok": True, "pages": pages, "coverage": module_coverage_from_pages(pages, project.get("portalType"))},
                )
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4]
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                page = get_page(project_id, code)
                if not page:
                    self.send_json(404, {"ok": False, "error": "页面不存在"})
                    return
                self.send_json(200, {"ok": True, "page": page})
                return
            if len(parts) == 6 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages" and parts[5] == "versions":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4]
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "versions": list_page_versions(project_id, code)})
                return

        if path == "/api/pages":
            project = get_deployed_content_project()
            pages = []
            if project:
                pages = [
                    page for page in list_pages(project["id"])
                    if page.get("qrAvailable") and page.get("id") in deployed_page_ids(project["id"])
                ]
            self.send_json(200, {"ok": True, "project": project, "pages": pages})
            return

        if path.startswith("/api/pages/"):
            code = path.rsplit("/", 1)[-1]
            project = get_deployed_content_project()
            page = get_display_page(project["id"], code, require_deployed=True) if project else None
            if not page:
                self.send_json(404, {"ok": False, "error": "页面不存在"})
                return
            self.send_json(200, {"ok": True, "project": project, "page": page})
            return

        if path == "/api/display/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-transform")
            self.send_header("Connection", "keep-alive")
            self.send_security_headers()
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            SSE_CLIENTS.add(self.wfile)
            try:
                while True:
                    time.sleep(15)
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except Exception:
                SSE_CLIENTS.discard(self.wfile)
            return

        if path.startswith("/static/"):
            self.serve_file(STATIC_DIR / path.removeprefix("/static/"))
            return

        if path.startswith("/uploads/"):
            self.serve_file(UPLOAD_DIR / path.removeprefix("/uploads/"))
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not self.require_csrf(path):
            return

        if path == "/api/login":
            data = self.read_json()
            username = str(data.get("username", "")).strip()
            password = str(data.get("password", ""))
            retry_after = rate_limit_retry_after(
                "login",
                f"{self.client_ip()}:{username.lower()}",
                LOGIN_RATE_LIMIT,
                LOGIN_RATE_WINDOW_SECONDS,
            )
            if retry_after:
                self.send_json(
                    429,
                    {"ok": False, "error": "登录尝试过多，请稍后再试"},
                    {"Retry-After": str(retry_after)},
                )
                return
            with db_connect() as conn:
                row = conn.execute(
                    "SELECT password_hash, enabled FROM users WHERE username = ?",
                    (username,),
                ).fetchone()
            if not row or not bool(row["enabled"]) or not verify_password(password, row["password_hash"]):
                self.send_json(401, {"ok": False, "error": "用户名或密码错误"})
                return
            token = create_admin_session(username)
            user = get_user(username)
            redirect_url = "/admin" if user["role"] == "admin" else "/teacher?view=pages"
            create_admin_log("login", "user", username, username, "login", username=username, role=user["role"], ip=self.client_ip())
            self.send_json(
                200,
                {"ok": True, "username": username, "user": user, "redirectUrl": redirect_url},
                {"Set-Cookie": self.session_cookie_header(token)},
            )
            return
        if path == "/api/logout":
            user = self.current_user() or {}
            username = user.get("username", "")
            delete_admin_session(self.cookie_value(ADMIN_COOKIE))
            create_admin_log("logout", "user", username, username, "logout", username=username, role=user.get("role", ""), ip=self.client_ip())
            self.send_json(
                200,
                {"ok": True},
                {"Set-Cookie": self.clear_session_cookie_header()},
            )
            return

        if path == "/api/account/password":
            user = self.require_auth()
            if not user:
                return
            data = self.read_json()
            try:
                change_password(user["username"], str(data.get("oldPassword", "")), str(data.get("newPassword", "")))
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.log_admin("change_password", "user", user["username"], user["displayName"], "password changed")
            self.send_json(200, {"ok": True})
            return

        if path == "/api/users":
            actor = self.require_admin()
            if not actor:
                return
            data = self.read_json()
            try:
                user = upsert_user(data, actor["username"])
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.log_admin("save_user", "user", user["username"], user["displayName"], "save user", changes="profile,password" if data.get("password") else "profile")
            self.send_json(200, {"ok": True, "user": user})
            return

        if path == "/api/users/import-csv":
            actor = self.require_admin()
            if not actor:
                return
            data = self.read_json()
            text_csv = str(data.get("csv") or "")
            result = {"created": 0, "updated": 0, "projects": 0, "errors": []}
            reader = csv.DictReader(io.StringIO(text_csv))
            for line_no, row in enumerate(reader, start=2):
                try:
                    username = str(row.get("username") or "").strip()
                    if not username:
                        raise ValueError("username 不能为空")
                    existed = get_user(username)
                    user = upsert_user({"username": username, "displayName": row.get("name") or row.get("displayName") or username, "password": row.get("password"), "department": row.get("department") or "", "role": "teacher", "enabled": True}, actor["username"])
                    result["updated" if existed else "created"] += 1
                    projects_text = str(row.get("projects") or "").strip()
                    for name in [item.strip() for item in re.split(r"[;；]", projects_text) if item.strip()]:
                        save_project(None, {"name": name, "ownerUsername": user["username"]}, actor)
                        result["projects"] += 1
                except Exception as exc:
                    result["errors"].append({"line": line_no, "error": str(exc)})
            self.log_admin("import_users", "user", "", "CSV import", json.dumps(result, ensure_ascii=False))
            self.send_json(200, {"ok": True, "result": result})
            return

        if path.startswith("/api/users/"):
            actor = self.require_admin()
            if not actor:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "users":
                username = parts[2]
                action = parts[3]
                data = self.read_json()
                try:
                    if action == "reset-password":
                        user = reset_user_password(username, data.get("password"))
                        log_action = "reset_password"
                    elif action == "disable":
                        user = set_user_enabled(username, False)
                        log_action = "disable_user"
                    elif action == "enable":
                        user = set_user_enabled(username, True)
                        log_action = "enable_user"
                    else:
                        user = None
                        log_action = ""
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                if not user:
                    self.send_json(404, {"ok": False, "error": "用户不存在"})
                    return
                self.log_admin(log_action, "user", user["username"], user["displayName"], log_action)
                self.send_json(200, {"ok": True, "user": user})
                return

        if path == "/api/lowcode/forms":
            actor = self.require_admin()
            if not actor:
                return
            try:
                form = save_lowcode_form(None, self.read_json(), actor)
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.log_admin("save_lowcode_form", "lowcode_form", form["id"], form["name"], "create form")
            self.send_json(200, {"ok": True, "form": form})
            return

        if path.startswith("/api/lowcode/forms/") and path.endswith("/copy"):
            actor = self.require_admin()
            if not actor:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "lowcode" and parts[2] == "forms" and parts[4] == "copy":
                form_id = int(parts[3]) if parts[3].isdigit() else 0
                try:
                    form = copy_lowcode_form(form_id, self.read_json(), actor)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                self.log_admin("copy_lowcode_form", "lowcode_form", form["id"], form["name"], f"copy from {form_id}")
                self.send_json(200, {"ok": True, "form": form})
                return

        if path == "/api/deploy/content":
            actor = self.require_admin()
            if not actor:
                return
            data = self.read_json()
            project_id = int(data.get("projectId") or 0)
            page_ids = data.get("pageIds")
            try:
                project = deploy_content_project(project_id, page_ids if isinstance(page_ids, list) else None)
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc), "check": deploy_content_check(project_id, page_ids if isinstance(page_ids, list) else None)})
                return
            if not project:
                self.send_json(404, {"ok": False, "error": "项目不存在"})
                return
            self.log_admin("deploy_content", "project", project["id"], project["name"], "deploy selected pages", changes="pageIds")
            self.send_json(200, {"ok": True, "project": project, "pageIds": deployed_page_ids(project_id)})
            return

        if path.startswith("/api/reviews/"):
            actor = self.require_admin()
            if not actor:
                return
            parts = path.strip("/").split("/")
            data = self.read_json()
            note = str(data.get("note") or "")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "reviews":
                review_type = parts[2]
                version_id = int(parts[3]) if parts[3].isdigit() else 0
                action = parts[4]
                if review_type == "pages" and action == "approve":
                    item = approve_page_version(version_id, actor, note)
                elif review_type == "pages" and action == "reject":
                    item = reject_page_version(version_id, actor, note)
                elif review_type == "projects" and action == "approve":
                    item = approve_project_version(version_id, actor, note)
                elif review_type == "projects" and action == "reject":
                    item = reject_project_version(version_id, actor, note)
                elif review_type == "content-items" and action == "approve":
                    item = approve_content_item_version(version_id, actor, note)
                elif review_type == "content-items" and action == "reject":
                    item = reject_content_item_version(version_id, actor, note)
                else:
                    item = None
                if not item:
                    self.send_json(404, {"ok": False, "error": "审核记录不存在"})
                    return
                self.log_admin(f"review_{action}", review_type[:-1], version_id, str(version_id), note)
                self.send_json(200, {"ok": True, "item": item})
                return

        if path.startswith("/api/projects/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "content-items":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                try:
                    item = save_content_item(project_id, None, self.read_json(), user, approve_now=user["role"] == "admin")
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                self.log_admin(
                    "save_content_item" if user["role"] == "admin" else "submit_content_item",
                    "content_item",
                    item["id"],
                    item["title"],
                    f"project {project_id}",
                    changes="structured-content",
                )
                self.send_json(200, {"ok": True, "item": item})
                return
            if len(parts) == 7 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "lowcode" and parts[4] == "forms" and parts[6] == "records":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                form_id = int(parts[5]) if parts[5].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                try:
                    result = submit_lowcode_record(project_id, form_id, self.read_json(), user)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                self.log_admin(
                    "submit_lowcode_record" if user["role"] != "admin" else "save_lowcode_record",
                    "lowcode_record",
                    result["record"]["id"],
                    result["item"]["title"],
                    f"project {project_id}",
                    changes="lowcode-to-content-item",
                )
                self.send_json(200, {"ok": True, **result})
                return

        if path.startswith("/api/content-items/") and path.endswith("/assets"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "content-items" and parts[3] == "assets":
                content_item_id = int(parts[2]) if parts[2].isdigit() else 0
                try:
                    item = add_content_item_asset(content_item_id, self.read_json(), user)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                if not item:
                    self.send_json(404, {"ok": False, "error": "资料不存在"})
                    return
                self.log_admin("link_content_asset", "content_item", item["id"], item["title"], "link asset")
                self.send_json(200, {"ok": True, "item": item})
                return
        if path == "/api/projects":
            actor = self.require_admin()
            if not actor:
                return
            project = save_project(None, self.read_json(), actor)
            self.log_admin("create_project", "project", project["id"], project["name"], "新建项目")
            self.send_json(200, {"ok": True, "project": project})
            return

        if path.startswith("/api/projects/"):
            actor = self.require_admin()
            if not actor:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "copy":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = copy_project(project_id, self.read_json())
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("copy_project", "project", project["id"], project["name"], f"复制来源项目 {project_id}")
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "deploy":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                try:
                    project = deploy_project(project_id)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc), "check": deploy_project_check(project_id)})
                    return
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("deploy_welcome", "project", project["id"], project["name"], "部署欢迎页")
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "deploy-content":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                try:
                    project = deploy_content_project(project_id)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc), "check": deploy_content_check(project_id)})
                    return
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("deploy_content", "project", project["id"], project["name"], "部署展示项目内容")
                self.send_json(200, {"ok": True, "project": project})
                return

        if path in ("/api/scan", "/api/scans"):
            global LAST_SCAN
            data = self.read_json()
            original_url = str(data.get("url", "")).strip()
            raw_url = normalize_scan_url(original_url)

            # 数字门户展厅联动（DESIGN.md 第 13 节）：
            # 扫码内容指向 /departments/<id> 或 /topics/<id>（二维码生成的是绝对 URL，需按 path 匹配），
            # 命中后广播相对路径给展厅大屏
            parsed_scan_url = urlparse(original_url)
            if parsed_scan_url.scheme in ("http", "https"):
                bp_path = parsed_scan_url.path
                bp_query = parsed_scan_url.query
            else:
                bp_path = original_url.split("?", 1)[0]
                bp_query = original_url.split("?", 1)[1] if "?" in original_url else ""
            bp_match = re.match(r"^/(?:departments|topics)/([a-z0-9-]+)$", bp_path)
            if bp_match:
                bp_section = re.search(r"(?:^|&)section=([a-z0-9-]+)", bp_query)
                bp_display_url = bp_path + (f"?section={bp_section.group(1)}" if bp_section else "")
                scan = {
                    "url": bp_display_url,
                    "originalUrl": original_url,
                    "displayUrl": bp_display_url,
                    "localDisplayUrl": bp_display_url,
                    "code": bp_match.group(1),
                    "project": None,
                    "page": None,
                    "external": True,
                    "result": "ok",
                    "detail": "blueprint",
                    "receivedAt": now_iso(),
                }
                LAST_SCAN = scan
                with db_connect() as conn:
                    conn.execute(
                        "INSERT INTO scans (code, raw_url, project_id, result, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (scan["code"], original_url, 0, "ok", "blueprint", scan["receivedAt"]),
                    )
                if self.current_user():
                    self.log_admin("simulate_scan", "page", scan["code"], scan["code"], original_url, changes="blueprint")
                try:
                    broadcast_scan(scan)
                except Exception:
                    SSE_CLIENTS.clear()
                self.send_json(200, {"ok": True, "scan": scan, "clients": len(SSE_CLIENTS)})
                return

            project_id, code = extract_scan_target(raw_url or original_url)
            if not code:
                self.send_json(400, {"ok": False, "error": "扫码内容无效"})
                return

            scanned_url = raw_url or original_url
            external_link = is_external_url(scanned_url)
            project = None
            page = None
            local_display_url = ""
            result = "ok"
            detail = ""
            project = get_deployed_content_project()
            if project and (not project_id or int(project_id) == int(project["id"])):
                matched_code, page = find_deployed_display_page(project["id"], code)
                if page:
                    code = matched_code
                    external_link = False
                    local_display_url = f"/display?project={project['id']}&code={code}"
                elif not external_link:
                    result = "not_available"
                    detail = "页面未通过审核、未勾选部署或账号已禁用"
            elif not external_link:
                result = "not_deployed"
                detail = "内容未部署到当前大屏"
                project = None
            target_display_url = scanned_url if external_link else local_display_url
            scan = {
                "url": scanned_url,
                "originalUrl": original_url,
                "displayUrl": target_display_url,
                "localDisplayUrl": local_display_url,
                "code": code,
                "project": project,
                "page": page,
                "external": external_link,
                "result": result,
                "detail": detail,
                "receivedAt": now_iso(),
            }
            LAST_SCAN = scan
            with db_connect() as conn:
                conn.execute(
                    "INSERT INTO scans (code, raw_url, project_id, result, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (code, raw_url or original_url, project["id"] if project else 0, result, detail, scan["receivedAt"]),
                )
            if self.current_user():
                self.log_admin("simulate_scan", "page", code, code, scanned_url, changes=result)
            if result == "ok":
                try:
                    broadcast_scan(scan)
                except Exception:
                    SSE_CLIENTS.clear()
            self.send_json(200, {"ok": True, "scan": scan, "clients": len(SSE_CLIENTS)})
            return
        if path == "/api/assets":
            user = self.require_auth()
            if not user:
                return
            retry_after = rate_limit_retry_after(
                "upload",
                f"{user.get('username', '')}:{self.client_ip()}",
                UPLOAD_RATE_LIMIT,
                UPLOAD_RATE_WINDOW_SECONDS,
            )
            if retry_after:
                self.send_json(
                    429,
                    {"ok": False, "error": "上传过于频繁，请稍后再试"},
                    {"Retry-After": str(retry_after)},
                )
                return
            data = self.read_json(max_bytes=max(MAX_JSON_BYTES, int(MAX_UPLOAD_BYTES * 1.5) + 1024))
            data_url = str(data.get("dataUrl", ""))
            filename = str(data.get("filename", "upload")).strip()
            match = re.match(r"data:(image/[a-zA-Z0-9.+-]+);base64,(.+)", data_url)
            if not match:
                self.send_json(400, {"ok": False, "error": "图片数据无效"})
                return

            mime, encoded = match.groups()
            ext = UPLOAD_MIME_EXTENSIONS.get(mime)
            if not ext:
                self.send_json(415, {"ok": False, "error": "不支持的图片类型"})
                return
            safe_name = f"{uuid.uuid4().hex}{ext}"
            storage_key = f"{ASSET_KEY_PREFIX}/{safe_name}" if ASSET_KEY_PREFIX else safe_name
            try:
                payload = base64.b64decode(encoded, validate=True)
                if len(payload) > MAX_UPLOAD_BYTES:
                    self.send_json(413, {"ok": False, "error": "上传图片太大"})
                    return
                url = asset_storage(UPLOAD_DIR).save(storage_key, payload, mime)
                asset = create_asset_record(user, filename, storage_key, url, mime, len(payload))
            except Exception as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return

            self.log_admin(
                "upload_asset",
                "asset",
                storage_key,
                filename,
                f"{mime} -> {url} ({asset_storage_backend()})",
            )
            self.send_json(200, {"ok": True, "url": url, "asset": asset})
            return

        self.send_error(404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not self.require_csrf(path):
            return

        if path.startswith("/api/projects/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                if user["role"] == "admin":
                    project = save_project(project_id, self.read_json(), user)
                    self.log_admin("update_project", "project", project["id"], project["name"], "update project", changes="config")
                else:
                    project = submit_project_config(project_id, self.read_json(), user)
                    self.log_admin("submit_project_config", "project", project["id"], project["name"], "submit project config", changes="config")
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "content-items":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                content_item_id = int(parts[4]) if parts[4].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                try:
                    item = save_content_item(project_id, content_item_id, self.read_json(), user, approve_now=user["role"] == "admin")
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                self.log_admin(
                    "save_content_item" if user["role"] == "admin" else "submit_content_item",
                    "content_item",
                    item["id"],
                    item["title"],
                    f"project {project_id}",
                    changes="structured-content",
                )
                self.send_json(200, {"ok": True, "item": item})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4].strip()
                if not code:
                    self.send_json(400, {"ok": False, "error": "code 不能为空"})
                    return
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                try:
                    page = save_page(project_id, code, self.read_json(), user, approve_now=user["role"] == "admin")
                except ValueError as exc:
                    self.send_json(409, {"ok": False, "error": str(exc)})
                    return
                self.log_admin("save_page" if user["role"] == "admin" else "submit_page", "page", page["code"], page["title"], f"project {project_id}", changes="content")
                self.send_json(200, {"ok": True, "page": page})
                return

        if path.startswith("/api/lowcode/forms/"):
            actor = self.require_admin()
            if not actor:
                return
            form_id_text = path.rsplit("/", 1)[-1]
            form_id = int(form_id_text) if form_id_text.isdigit() else 0
            try:
                form = save_lowcode_form(form_id, self.read_json(), actor)
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.log_admin("update_lowcode_form", "lowcode_form", form["id"], form["name"], "update form")
            self.send_json(200, {"ok": True, "form": form})
            return

        if path.startswith("/api/pages/"):
            user = self.require_auth()
            if not user:
                return
            code = path.rsplit("/", 1)[-1].strip()
            if not code:
                self.send_json(400, {"ok": False, "error": "code 不能为空"})
                return
            project = get_deployed_content_project()
            if not project or not project_accessible(project, user):
                self.send_json(500, {"ok": False, "error": "当前没有已部署的内容项目"})
                return
            try:
                page = save_page(project["id"], code, self.read_json(), user, approve_now=user["role"] == "admin")
            except ValueError as exc:
                self.send_json(409, {"ok": False, "error": str(exc)})
                return
            self.log_admin("save_page" if user["role"] == "admin" else "submit_page", "page", page["code"], page["title"], f"project {project['id']}", changes="content")
            self.send_json(200, {"ok": True, "page": page})
            return

        if path.startswith("/api/content-items/") and path.endswith("/assets/order"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "content-items" and parts[3] == "assets" and parts[4] == "order":
                content_item_id = int(parts[2]) if parts[2].isdigit() else 0
                data = self.read_json()
                try:
                    item = reorder_content_item_assets(content_item_id, data.get("assets") if isinstance(data.get("assets"), list) else [], user)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                if not item:
                    self.send_json(404, {"ok": False, "error": "资料不存在"})
                    return
                self.log_admin("order_content_assets", "content_item", item["id"], item["title"], "order assets")
                self.send_json(200, {"ok": True, "item": item})
                return
        self.send_error(404)
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not self.require_csrf(path):
            return

        if path.startswith("/api/projects/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
                if user["role"] != "admin":
                    self.send_json(403, {"ok": False, "error": "没有权限执行此操作"})
                    return
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not delete_project(project_id):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("delete_project", "project", project_id, project["name"] if project else "", "delete project")
                self.send_json(200, {"ok": True})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "content-items":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                content_item_id = int(parts[4]) if parts[4].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                item = delete_content_item(project_id, content_item_id, user, approve_now=user["role"] == "admin")
                if not item:
                    self.send_json(404, {"ok": False, "error": "资料不存在"})
                    return
                self.log_admin(
                    "delete_content_item" if user["role"] == "admin" else "request_delete_content_item",
                    "content_item",
                    item["id"],
                    item["title"],
                    f"project {project_id}",
                )
                self.send_json(200, {"ok": True, "item": item})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4].strip()
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                ok = request_delete_page(project_id, code, user, approve_now=user["role"] == "admin")
                if not ok:
                    self.send_json(404, {"ok": False, "error": "页面不存在"})
                    return
                self.log_admin("delete_page" if user["role"] == "admin" else "request_delete_page", "page", code, code, f"project {project_id}")
                self.send_json(200, {"ok": True})
                return

        if path.startswith("/api/content-items/") and "/assets/" in path:
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "content-items" and parts[3] == "assets":
                content_item_id = int(parts[2]) if parts[2].isdigit() else 0
                try:
                    item = delete_content_item_asset(content_item_id, parts[4], user)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                if not item:
                    self.send_json(404, {"ok": False, "error": "资料不存在"})
                    return
                self.log_admin("unlink_content_asset", "content_item", item["id"], item["title"], "unlink asset")
                self.send_json(200, {"ok": True, "item": item})
                return

        if path.startswith("/api/assets/"):
            user = self.require_auth()
            if not user:
                return
            asset_id_text = path.rsplit("/", 1)[-1]
            asset_id = int(asset_id_text) if asset_id_text.isdigit() else 0
            try:
                asset = delete_asset(asset_id, user)
            except Exception as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            if not asset:
                self.send_json(404, {"ok": False, "error": "资源不存在"})
                return
            self.log_admin("delete_asset", "asset", asset["id"], asset["originalFilename"], asset["url"])
            self.send_json(200, {"ok": True, "asset": asset})
            return

        self.send_error(404)

def main():
    validate_runtime_config()
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), ExpoHandler)
    print(f"Expo display server running at http://{HOST}:{PORT}")
    print(f"Display: http://{HOST}:{PORT}/display")
    print(f"Admin:   http://{HOST}:{PORT}/admin")
    server.serve_forever()


if __name__ == "__main__":
    main()
