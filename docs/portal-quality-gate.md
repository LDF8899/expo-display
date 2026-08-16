# 门户质量检查

每次修改学校门户、系部门户、专题门户、后台发布逻辑、成果超市边界或部署打包规则后，建议运行：

```powershell
python .\scripts\portal_quality_gate.py
```

Windows 现场维护也可以直接双击：

```text
运行门户质量检查.bat
```

## 检查范围

质量门禁会按顺序检查：

- 工具链：确认 Python、Node.js、npx 可用。
- Python 编译：检查 `server.py` 和门户相关测试脚本是否存在语法错误。
- 前端语法：检查 `static/admin.js` 和 `static/blueprint/blueprint.js`。
- 蓝图数据：检查系部和专题 JSON、素材引用、占位文案。
- 前端静态安全：禁止内联 `<script>`、内联事件、`javascript:` URL 等不利于 CSP 的写法。
- 静态资源缓存：HTML 引用 `/static/*.css` 和 `/static/*.js` 必须带 `?v=`，同一页面内同组 CSS/JS 版本号必须一致，避免浏览器继续使用旧样式或旧脚本。
- 公共门户接口：确认只返回已审核、启用的公开资料，且统计数量一致。
- 二维码边界：只允许 `/display` 欢迎页和 `/departments` 学校门户显示学校官网二维码；系部、专题和扫码详情页不显示。
- 系部页布局：检查 `/departments/finance` 在桌面端保持左右分栏，在窄屏下顶部栏和系部下拉可用，并且页面没有横向溢出。
- 后台路径呈现：检查“门户管理”“板块资料”“展厅发布”都能显示学校、系部、专题的完整前台路径。
- 后台维护闭环：检查从后台总览点击门户完成度卡片后，能进入对应门户并自动生成标准板块草稿。
- 部署包完整性：确认 `expo-display-deploy.zip` 包含启动脚本、质量检查脚本、门户脚本、素材和文档，同时排除备份、缓存和调试输出。

## 通过标志

全部通过时，最后会输出：

```text
portal_quality_gate_ok=true
```

关键子项包括：

```text
qr_boundary_ok=true
department_layout_ok=true
admin_route_table_ok=true
admin_completion_workflow_ok=true
package_integrity_ok=true
```

## 失败处理

如果失败，脚本会停在第一个失败项，并输出对应检查名称。先按该项日志修复，再重新运行质量门禁。

注意：不要在运行质量门禁的同时重新打包，因为门禁会读取 `expo-display-deploy.zip`。如果打包正在重写 zip，完整性检查可能读到半写入文件。
