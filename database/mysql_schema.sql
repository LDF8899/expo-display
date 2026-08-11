CREATE DATABASE IF NOT EXISTS expo_display
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE expo_display;

CREATE TABLE IF NOT EXISTS users (
  username VARCHAR(64) PRIMARY KEY,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(120) NOT NULL DEFAULT '',
  role VARCHAR(32) NOT NULL DEFAULT 'teacher',
  department VARCHAR(120) NOT NULL DEFAULT '',
  enabled TINYINT(1) NOT NULL DEFAULT 1,
  created_at VARCHAR(40) NOT NULL,
  updated_at VARCHAR(40) NOT NULL,
  INDEX idx_users_role_enabled (role, enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS user_sessions (
  token VARCHAR(128) PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  expires_at BIGINT NOT NULL,
  created_at VARCHAR(40) NOT NULL,
  INDEX idx_user_sessions_username (username),
  INDEX idx_user_sessions_expires_at (expires_at),
  CONSTRAINT fk_user_sessions_user
    FOREIGN KEY (username) REFERENCES users(username)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS admin_users (
  username VARCHAR(64) PRIMARY KEY,
  password_hash VARCHAR(255) NOT NULL,
  updated_at VARCHAR(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS admin_sessions (
  token VARCHAR(128) PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  expires_at BIGINT NOT NULL,
  created_at VARCHAR(40) NOT NULL,
  INDEX idx_admin_sessions_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS projects (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(180) NOT NULL,
  portal_type VARCHAR(32) NOT NULL DEFAULT 'department',
  portal_slug VARCHAR(160) NOT NULL DEFAULT '',
  idle_kicker VARCHAR(120) NOT NULL DEFAULT '学校简介',
  idle_title VARCHAR(255) NOT NULL DEFAULT '欢迎来到毕节职业技术学院',
  idle_copy TEXT NOT NULL,
  welcome_kicker VARCHAR(120) NOT NULL DEFAULT 'Welcome',
  welcome_title VARCHAR(255) NOT NULL DEFAULT '欢迎参观 {title}',
  welcome_subtitle VARCHAR(255) NOT NULL DEFAULT '即将进入展示页面',
  default_image_url VARCHAR(1024) NOT NULL DEFAULT '/static/expo-stage.png',
  accent VARCHAR(32) NOT NULL DEFAULT '#f59a13',
  display_config JSON NOT NULL,
  deployed TINYINT(1) NOT NULL DEFAULT 0,
  content_deployed TINYINT(1) NOT NULL DEFAULT 0,
  deployed_at VARCHAR(40) NOT NULL DEFAULT '',
  content_deployed_at VARCHAR(40) NOT NULL DEFAULT '',
  owner_username VARCHAR(64) NOT NULL DEFAULT 'admin',
  config_status VARCHAR(32) NOT NULL DEFAULT 'approved',
  pending_config_version_id BIGINT NULL,
  updated_at VARCHAR(40) NOT NULL,
  INDEX idx_projects_owner (owner_username),
  INDEX idx_projects_portal (portal_type, portal_slug),
  INDEX idx_projects_deployed (deployed),
  INDEX idx_projects_content_deployed (content_deployed),
  INDEX idx_projects_config_status (config_status),
  CONSTRAINT fk_projects_owner
    FOREIGN KEY (owner_username) REFERENCES users(username)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS pages (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_id BIGINT NOT NULL,
  code VARCHAR(160) NOT NULL,
  category VARCHAR(120) NOT NULL DEFAULT '校园新闻',
  source VARCHAR(160) NOT NULL DEFAULT '学校展示',
  published_at VARCHAR(80) NOT NULL DEFAULT '',
  title VARCHAR(255) NOT NULL,
  subtitle VARCHAR(512) NOT NULL DEFAULT '',
  body MEDIUMTEXT NOT NULL,
  image_url VARCHAR(1024) NOT NULL DEFAULT '',
  content_type VARCHAR(32) NOT NULL DEFAULT 'article',
  accent VARCHAR(32) NOT NULL DEFAULT '#0f766e',
  enabled TINYINT(1) NOT NULL DEFAULT 1,
  review_status VARCHAR(32) NOT NULL DEFAULT 'approved',
  pending_version_id BIGINT NULL,
  submitted_by VARCHAR(64) NOT NULL DEFAULT 'admin',
  reviewed_by VARCHAR(64) NOT NULL DEFAULT 'admin',
  review_note VARCHAR(1024) NOT NULL DEFAULT '',
  updated_at VARCHAR(40) NOT NULL,
  UNIQUE KEY uq_pages_project_code (project_id, code),
  INDEX idx_pages_project_status (project_id, review_status),
  INDEX idx_pages_code (code),
  CONSTRAINT fk_pages_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_pages_submitted_by
    FOREIGN KEY (submitted_by) REFERENCES users(username)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS page_versions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  page_id BIGINT NULL,
  project_id BIGINT NOT NULL,
  code VARCHAR(160) NOT NULL,
  operation VARCHAR(32) NOT NULL DEFAULT 'upsert',
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  snapshot JSON NOT NULL,
  submitted_by VARCHAR(64) NOT NULL DEFAULT '',
  submitted_at VARCHAR(40) NOT NULL,
  reviewed_by VARCHAR(64) NOT NULL DEFAULT '',
  reviewed_at VARCHAR(40) NOT NULL DEFAULT '',
  review_note VARCHAR(1024) NOT NULL DEFAULT '',
  changes VARCHAR(2048) NOT NULL DEFAULT '',
  INDEX idx_page_versions_status (status, submitted_at),
  INDEX idx_page_versions_project (project_id),
  INDEX idx_page_versions_page (page_id),
  CONSTRAINT fk_page_versions_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_page_versions_page
    FOREIGN KEY (page_id) REFERENCES pages(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS project_versions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_id BIGINT NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  snapshot JSON NOT NULL,
  submitted_by VARCHAR(64) NOT NULL DEFAULT '',
  submitted_at VARCHAR(40) NOT NULL,
  reviewed_by VARCHAR(64) NOT NULL DEFAULT '',
  reviewed_at VARCHAR(40) NOT NULL DEFAULT '',
  review_note VARCHAR(1024) NOT NULL DEFAULT '',
  changes VARCHAR(2048) NOT NULL DEFAULT '',
  INDEX idx_project_versions_status (status, submitted_at),
  INDEX idx_project_versions_project (project_id),
  CONSTRAINT fk_project_versions_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS deployed_pages (
  project_id BIGINT NOT NULL,
  page_id BIGINT NOT NULL,
  updated_at VARCHAR(40) NOT NULL,
  PRIMARY KEY (project_id, page_id),
  CONSTRAINT fk_deployed_pages_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_deployed_pages_page
    FOREIGN KEY (page_id) REFERENCES pages(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS achievement_market_config (
  id TINYINT PRIMARY KEY DEFAULT 1,
  welcome_title VARCHAR(255) NOT NULL DEFAULT '成果超市',
  welcome_subtitle VARCHAR(255) NOT NULL DEFAULT '',
  welcome_intro TEXT NOT NULL,
  welcome_image_url VARCHAR(1024) NOT NULL DEFAULT '',
  welcome_note VARCHAR(255) NOT NULL DEFAULT '',
  updated_at VARCHAR(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS achievement_market_items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_id BIGINT NOT NULL,
  page_id BIGINT NOT NULL,
  category_key VARCHAR(40) NOT NULL,
  intro VARCHAR(512) NOT NULL DEFAULT '',
  sort_order INT NOT NULL DEFAULT 0,
  enabled TINYINT(1) NOT NULL DEFAULT 1,
  created_at VARCHAR(40) NOT NULL,
  updated_at VARCHAR(40) NOT NULL,
  UNIQUE KEY uq_achievement_market_page (page_id),
  INDEX idx_achievement_market_project (project_id, enabled, sort_order),
  INDEX idx_achievement_market_category (category_key, enabled, sort_order),
  CONSTRAINT fk_achievement_market_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_achievement_market_page
    FOREIGN KEY (page_id) REFERENCES pages(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS scans (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(160) NOT NULL,
  raw_url VARCHAR(2048) NOT NULL,
  project_id BIGINT NOT NULL DEFAULT 0,
  result VARCHAR(40) NOT NULL DEFAULT 'ok',
  detail TEXT NOT NULL,
  created_at VARCHAR(40) NOT NULL,
  INDEX idx_scans_created_at (created_at),
  INDEX idx_scans_project (project_id),
  INDEX idx_scans_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS admin_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL DEFAULT '',
  role VARCHAR(32) NOT NULL DEFAULT '',
  action VARCHAR(80) NOT NULL,
  target_type VARCHAR(80) NOT NULL DEFAULT '',
  target_id VARCHAR(120) NOT NULL DEFAULT '',
  target_label VARCHAR(255) NOT NULL DEFAULT '',
  detail TEXT NOT NULL,
  changes VARCHAR(2048) NOT NULL DEFAULT '',
  ip VARCHAR(80) NOT NULL DEFAULT '',
  created_at VARCHAR(40) NOT NULL,
  INDEX idx_admin_logs_created_at (created_at),
  INDEX idx_admin_logs_username (username),
  INDEX idx_admin_logs_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS assets (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  owner_username VARCHAR(64) NOT NULL DEFAULT '',
  original_filename VARCHAR(255) NOT NULL DEFAULT '',
  storage_key VARCHAR(1024) NOT NULL,
  url VARCHAR(2048) NOT NULL,
  mime_type VARCHAR(120) NOT NULL DEFAULT '',
  size_bytes BIGINT NOT NULL DEFAULT 0,
  backend VARCHAR(40) NOT NULL DEFAULT 'local',
  created_at VARCHAR(40) NOT NULL,
  INDEX idx_assets_owner_created (owner_username, created_at),
  INDEX idx_assets_created_at (created_at),
  CONSTRAINT fk_assets_owner
    FOREIGN KEY (owner_username) REFERENCES users(username)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
  CONSTRAINT fk_content_items_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_content_items_page
    FOREIGN KEY (page_id) REFERENCES pages(id)
    ON DELETE SET NULL,
  CONSTRAINT fk_content_items_cover
    FOREIGN KEY (cover_asset_id) REFERENCES assets(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
  CONSTRAINT fk_content_item_assets_item
    FOREIGN KEY (content_item_id) REFERENCES content_items(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_content_item_assets_asset
    FOREIGN KEY (asset_id) REFERENCES assets(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
  CONSTRAINT fk_content_item_versions_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_content_item_versions_item
    FOREIGN KEY (content_item_id) REFERENCES content_items(id)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
