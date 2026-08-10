from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "role admin helper": 'function isAdmin() { return state.user && state.user.role === "admin"; }' in js,
        "role department helper": 'function isDepartmentAdmin() { return state.user && state.user.role === "department_admin"; }' in js,
        "role reviewer helper": "function canReview() { return isAdmin() || isDepartmentAdmin(); }" in js,
        "role teacher helper": "function isTeacherPortal() { return !canReview(); }" in js,
        "admin nav order": 'return isAdmin() ? ["dashboard", "projects", "pages", "assets", "reviews", "reports", "settings"]' in js,
        "admin internal views": '["dashboard", "projects", "pages", "assets", "reviews", "reports", "settings", "users", "deploy", "logs", "account"]' in js,
        "department nav order": "canReview() ? reviewerViewOrder : teacherViewOrder" in js,
        "reviewer nav excludes global admin": 'const reviewerViewOrder = ["dashboard", "projects", "pages", "assets", "reviews", "reports", "account"]' in js,
        "teacher nav order": 'const teacherViewOrder = ["pages", "assets", "projects", "account"]' in js,
        "teacher nav labels": 'const teacherViews = {' in js and 'projects: ["我的门户"' in js,
        "teacher portal class": 'document.body.classList.toggle("teacher-portal", isTeacherPortal())' in js,
        "admin only hidden by admin": 'document.querySelectorAll(".admin-only").forEach((node) => { node.hidden = !isAdmin(); });' in js,
        "review view open to reviewers": '$("reviewsView").hidden = !canReview();' in js,
        "review view exists": 'id="reviewsView"' in html and '审核发布' in html,
        "teacher console title": 'canReview() ? "数字门户后台" : "门户资料工作台"' in js,
        "teacher submit copy": 'canReview() ? "保存/提交审核" : "提交审核"' in js,
        "teacher hides quality panels": '".content-quality-panel"' in js and '".lowcode-report-panel"' in js,
        "teacher hides structured editor": '".structured-panel"' in js and '"#legacyPagesTableWrap"' in js,
        "teacher hides manual controls": '"newPage", "newLegacyPage", "pageStatusFilter", "exportModuleCoverage", "exportModuleGaps"' in js,
        "management fetch gated": "const loadManagementReports = canReview();" in js,
        "teacher still loads forms": "jsonApi(`/api/projects/${projectId}/lowcode/forms`)" in js,
        "teacher still loads records": "jsonApi(`/api/projects/${projectId}/lowcode/records`)" in js,
        "template create admin only": '$("newLowcodeTemplate").hidden = !isAdmin()' in js,
        "template import admin only": '$("importLowcodeTemplate").hidden = !isAdmin()' in js,
        "template edit admin only": '${isAdmin() ? `<button class="button small" type="button" data-lowcode-edit=' in js,
        "template fill visible": 'data-lowcode-start="${form.id}"' in js,
        "quality export reviewer only": '$("exportLowcodeTemplateQuality").hidden = !showTemplateQuality' in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"role boundary static checks missing: {', '.join(missing)}")
    print("role_boundary_static_ok=true")


if __name__ == "__main__":
    main()
