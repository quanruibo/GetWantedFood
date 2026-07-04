# 项目验证补强计划

- 文档角色：`current_fact`
- 适用项目：`Get_wanted_food`
- 作用：记录当前验证覆盖缺口、优先补强方向与实施入口

## 1. 当前判断

- workspace 控制面验证通常较完整。
- 项目 active 主路径应有核心回归。
- 真实端到端业务语义、矩阵覆盖完整性和任务记录生命周期验证，通常是最常见缺口。

## 2. 优先级

### P1：结构完整性

- 建立任务记录生命周期校验
- 建立关键路径到矩阵规则的覆盖审计
- 将 active 测试库存与测试文档库存对齐

### P2：业务语义保护

- 建立固定小数据集 E2E 金样本回测
- 为产物 manifest / summary / report contract 增加更强回归

### P3：历史兼容与手动路径

- 明确 legacy/manual smoke 的补跑触发条件
- 逐步决定哪些 legacy 路径需要恢复为现行自动验证

## 3. 项目应记录的已落地项

- 当前项目已经落地的覆盖审计脚本或测试
- 当前项目已经补齐的 active 测试库存同步
- 当前项目尚未完成但已规划的验证补强项

## 4. 后续入口

- 项目级覆盖审计：由项目自己的验证工具承担
- 项目级验证编排：优先通过 `project_governance/CHANGE_SYNC_MATRIX.yaml` 与项目 runner 决定
- workspace 验证：`uv run python .governance/scripts/validation/run_full_validation.py`
