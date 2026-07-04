# 项目治理中间层

- 文档角色：`route`
- 作用：项目层“需求 -> 任务 -> 文档/测试同步 -> 验证 -> 升级到 workspace”的中间协作入口

## 先看哪里

1. `./TASK_RECORD_POLICY.md`
2. `./VALIDATION_HARDENING_PLAN.md`
3. `./CHANGE_SYNC_MATRIX.yaml`
4. `./task_records/README.md`
5. `../VALIDATION.md`

## 目录说明

- `TASK_RECORD_POLICY.md`：项目级 task record 生命周期、归档与校验政策
- `VALIDATION_HARDENING_PLAN.md`：当前验证覆盖缺口、补强优先级与实施入口
- `CHANGE_SYNC_MATRIX.yaml`：项目变更同步矩阵
- `task_records/`：项目级轻量任务记录层；只保留 `active/`、`done/` 与模板/索引
- `artifacts/latest/`：当前项目治理验证摘要、补强报告与审计证据

## 分层边界

- 项目层负责项目事实、规格、项目验证、项目任务记录与项目验收证据。
- workspace 层负责控制面、工单生命周期、升级判断与模板化吸收。
- 任务与工单数量按边界、风险和收口需要决定，不以数量最少为目标；必要时可以拆分多个任务或多个工单。
