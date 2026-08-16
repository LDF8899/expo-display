from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "module coverage button": 'id="exportModuleCoverage"' in html,
        "module coverage function": "function exportModuleCoverageCsv()" in js,
        "module coverage listener": '$("exportModuleCoverage").addEventListener("click", exportModuleCoverageCsv)' in js,
        "module coverage filename": "标准板块覆盖" in js,
        "module gaps button": 'id="exportModuleGaps"' in html,
        "module gaps function": "function exportModuleGapsCsv()" in js,
        "module gaps listener": '$("exportModuleGaps").addEventListener("click", exportModuleGapsCsv)' in js,
        "module gaps filename": "待补资料清单" in js,
        "content quality button": 'id="exportContentQuality"' in html,
        "content quality function": "function exportContentQualityCsv()" in js,
        "content quality listener": '$("exportContentQuality").addEventListener("click", exportContentQualityCsv)' in js,
        "content quality filename": "资料质量检查" in js,
        "asset archive button": 'id="exportAssetArchive"' in html,
        "asset archive function": "function exportAssetArchiveCsv()" in js,
        "asset archive listener": '$("exportAssetArchive").addEventListener("click", exportAssetArchiveCsv)' in js,
        "asset archive filename": "素材附件归档" in js,
        "lowcode report button": 'id="exportLowcodeReport"' in html,
        "lowcode report function": "function exportLowcodeReportCsv()" in js,
        "lowcode report listener": '$("exportLowcodeReport").addEventListener("click", exportLowcodeReportCsv)' in js,
        "lowcode report filename": "资料填报统计" in js,
        "lowcode reminder button": 'id="exportLowcodeReminderReport"' in html,
        "lowcode reminder function": "function exportLowcodeReminderReportCsv()" in js,
        "lowcode reminder listener": '$("exportLowcodeReminderReport").addEventListener("click", exportLowcodeReminderReportCsv)' in js,
        "lowcode reminder filename": "资料采集提醒" in js,
        "lowcode records button": 'id="exportLowcodeRecords"' in html,
        "lowcode records function": "function exportLowcodeRecordsCsv()" in js,
        "lowcode records listener": '$("exportLowcodeRecords").addEventListener("click", exportLowcodeRecordsCsv)' in js,
        "lowcode records filename": "模板提交记录" in js,
        "lowcode record details button": 'id="exportLowcodeRecordDetails"' in html,
        "lowcode record details function": "function exportLowcodeRecordDetailsCsv()" in js,
        "lowcode record details listener": '$("exportLowcodeRecordDetails").addEventListener("click", exportLowcodeRecordDetailsCsv)' in js,
        "lowcode record details filename": "模板填报明细" in js,
        "csv bom": "`\\uFEFF${[headers, ...rows]" in js or "`\\uFEFF${[headers, ...bodyRows]" in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"management report exports missing: {', '.join(missing)}")
    print("management_report_exports_static_ok=true")


if __name__ == "__main__":
    main()
