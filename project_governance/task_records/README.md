# 项目任务记录层

- 文档角色：`route`
- 作用：项目级轻量任务记录层，不替代 workspace work order

## 使用原则

- 项目内部需要持续跟踪时，可在这里记录任务。
- `task_records/active/` 只放 `planned` / `in_progress`。
- `task_records/done/` 只放近期完成、仍可能被回看的项目任务。
- 稳定吸收后只剩追溯价值的记录，应迁到 `.governance/archives/imported_projects/Get_wanted_food/project_governance/task_records/`。
- 若任务触碰 `.governance/`、loader、registry、工单生命周期、sync trigger matrix 或 cleanup / hygiene，应升级或关联到 workspace work order。
- 任务与工单数量按边界、风险和收口需要决定，不以数量最少为目标。
