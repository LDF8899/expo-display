from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "filter control": 'id="reviewStatusFilter"' in html,
        "approved option": '<option value="approved">已通过/已发布</option>' in html,
        "rejected option": '<option value="rejected">已退回</option>' in html,
        "state field": 'reviewStatusFilter: "pending"' in js,
        "api uses status": 'jsonApi(`/api/reviews?status=${encodeURIComponent(status)}`)' in js,
        "batch hidden outside pending": '$("batchApprove").hidden = status !== "pending"' in js,
        "history hides actions": '${status === "pending" ? `<button class="button small primary" data-review-approve=' in js,
        "change listener": '$("reviewStatusFilter").addEventListener("change"' in js,
        "batch guard": 'if (state.reviewStatusFilter !== "pending") return;' in js,
        "review note": "审核意见：" in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"review status filter missing: {', '.join(missing)}")
    print("review_status_filter_static_ok=true")


if __name__ == "__main__":
    main()
