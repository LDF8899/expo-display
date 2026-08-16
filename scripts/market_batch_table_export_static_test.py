from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"
ADMIN_CSS = ROOT / "static" / "admin.css"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    css = ADMIN_CSS.read_text(encoding="utf-8")
    category_head = html.split('class="market-workspace-head market-category-workspace-head"', 1)[1].split('id="marketCategoryTabs"', 1)[0]
    card_panel = html.split('id="marketBatchExportPanel"', 1)[1].split('id="marketTableExportPanel"', 1)[0]
    table_panel = html.split('id="marketTableExportPanel"', 1)[1].split('id="logsView"', 1)[0]
    old_table_ids = [
        "openMarketBatchTableExport",
        "marketBatchTableExportPanel",
        "marketBatchTableRows",
        "downloadSelectedMarketTable",
        "selectAllMarketTableItems",
        "selectCurrentMarketTableItems",
        "clearMarketTableItems",
    ]
    checks = {
        "separate top entries": 'id="openMarketTableExport"' in category_head and 'id="openMarketBatchExport"' in category_head,
        "card modal stays card-only": 'id="downloadSelectedMarketCards"' in card_panel and 'id="downloadMarketTable"' not in card_panel and 'id="marketTableRows"' not in card_panel,
        "separate table modal": 'id="marketTableExportPanel"' in html and all(token in table_panel for token in ['id="marketTableRows"', 'id="downloadMarketTable"']),
        "no card-like table picker": 'id="marketTableList"' not in html and "market-table-export-item" not in js and "market-table-export-item" not in css,
        "one click select all": 'id="selectAllMarketTableRows"' in table_panel,
        "table columns": all(label in js for label in ["展示块", "印在卡片上的文字", "二维码"]),
        "old table ids removed": not any(old_id in html or old_id in js for old_id in old_table_ids),
        "split table state": "marketTableSelectedIds" in js and "function selectedMarketTableItems" in js,
        "table starts empty": "function openMarketTableExport" in js and "state.marketTableSelectedIds = [];" in js and "默认未选择记录" in js,
        "row builder": "function marketTableRows" in js,
        "qr image builder": "function marketQrImageUrl" in js and "/api/qr-public?format=png" in js,
        "embedded excel export": "function buildMarketTableExcel" in js and "createXlsxZip" in js and ".xlsx" in js and "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in js,
        "qr embedded visibly": 'label: "二维码", width: 22, kind: "qr"' in js and 'Target="/xl/media/qr${image.index}.png"' in js and "二维码生成失败" in js,
        "open table modal": "function openMarketTableExport" in js and '$("openMarketTableExport").addEventListener("click", openMarketTableExport)' in js,
        "button listener": '$("downloadMarketTable").addEventListener("click"' in js,
        "table row picker": '$("marketTableRows").addEventListener("change"' in js and 'data-market-table-id' in js,
        "preview render on selection": "renderMarketTableList();" in js and "renderMarketTablePreview();" in js,
        "table status isolated": "marketTableStatus" in js,
        "table styling": ".market-table-preview" in css and ".market-table-qr img" in css,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"market batch table export missing: {', '.join(missing)}")
    print("market_batch_table_export_static_ok=true")


if __name__ == "__main__":
    main()
