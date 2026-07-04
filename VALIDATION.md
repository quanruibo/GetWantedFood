# Get_wanted_food Validation

- 文档角色：`route`
- 角色说明：项目级验证入口；当前项目以单脚本 CLI `./uiuc_dining_scan.py` 为主
- 默认上下文装载：`uv run python .governance/scripts/workspace/load_context.py --action modify --project Get_wanted_food --format text`
- import 入口：`uv run python .governance/scripts/workspace/import_project.py Get_wanted_food`
- 项目验证规则：`.governance/governance/10_PROJECT_VALIDATION_AND_TESTING.md`

## 1. 推荐阅读顺序

1. `./CURRENT_SPEC.md`
2. `./AGENTS.md`
3. `./tests/README.md`
4. `./design_docs/README.md`
5. `./design_docs/CLI.md`
6. `./design_docs/TEST_PLAN.md`
7. `./project_governance/README.md`
8. `.governance/governance/10_PROJECT_VALIDATION_AND_TESTING.md`

## 2. 当前最小验证

- 入口/路由回归：`uv run python -m pytest projects/Get_wanted_food/tests/test_validation_entry.py`
- 若只改 `README.md`、`AGENTS.md`、`CURRENT_SPEC.md`、`VALIDATION.md`、`tests/README.md` 或 `design_docs/*.md`，优先跑这条最小回归
- 若改 `uiuc_dining_scan.py` 的 CLI 参数、日期解析、CSV 输出或 Playwright 扫描逻辑，再补充对应的 targeted project tests

## 3. 文档联动

- 改 CLI 参数、输出格式或使用方法：同步回查 `./README.md`、`./design_docs/CLI.md`、`./design_docs/TEST_PLAN.md`
- 改测试入口或测试选择：同步回查 `./tests/README.md` 与 `./project_governance/CHANGE_SYNC_MATRIX.yaml`
- 改 imported project 近处入口或旧治理残留处理：回查 `.governance/governance/09_IMPORTED_PROJECT_NORMALIZATION.md`
- 若改动触碰 `.governance/`、registry、loader 或 workspace gate，再补跑 workspace validation

## 4. 风险提示

- 当前项目还没有覆盖 Playwright 真机扫描的完整自动化回归；现有最小测试先保证入口与文档路由稳定
- 本文件只负责项目验证路由，不替代 workspace validation
