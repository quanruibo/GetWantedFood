# Tests

- 文档角色：`route`
- 当前最小入口回归：`tests/test_validation_entry.py`
- `smoke/`：后续可放轻量 CLI smoke
- `regression/`：后续放长期回归

优先顺序：

1. 改项目近处入口、验证路由或 CLI 使用说明：先跑 `uv run python -m pytest projects/Get_wanted_food/tests/test_validation_entry.py`
2. 改 `uiuc_dining_scan.py` 的扫描逻辑或输出结构：在本文件基础上补 targeted project tests
3. 若改动触碰 `.governance/` 或 registry，再补跑 workspace validation
