# Test Plan

- 当前阶段：import onboarding 后的最小验证
- 当前最小目标：先保证项目入口、CLI 文档路由与验证入口稳定

## 当前必跑

- `uv run python -m pytest projects/Get_wanted_food/tests/test_validation_entry.py`

## 后续补强方向

- 为 `clean()`、`parse_start_date()`、`extract_date_from_mealperiod()` 增加纯函数测试
- 在可稳定提供 Playwright 运行环境后，增加 CLI / CSV 输出 smoke
- 若项目开始沉淀更多业务规则，再把扫描逻辑拆成更易测的模块
