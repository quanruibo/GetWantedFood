# 项目级 Task Record 生命周期政策

- 文档角色：`current_fact`
- 适用项目：`Get_wanted_food`
- 作用：定义项目级 `task_records/` 的状态、目录、archive 边界与校验入口

## 1. 目的

- 为项目内部轻量任务持续化提供稳定结构。
- 避免 `task_records/` 长期堆积一次性材料，污染 live surface。
- 明确它与 workspace `work_orders/` 的边界。

## 2. 本地目录模型

- `project_governance/task_records/active/`：当前正在推进的项目任务记录
- `project_governance/task_records/done/`：近期完成、仍可能被回看的项目任务记录
- `project_governance/task_records/TASK_RECORD.template.yaml`：任务记录模板
- `project_governance/task_records/README.md`：任务记录层入口

项目 live surface 不保留本地 `archived/` 或 `abandoned/` 目录。

## 3. 状态模型

- `planned`：任务已建档，尚未进入主体实施；必须位于 `active/`
- `in_progress`：任务正在推进；必须位于 `active/`
- `done`：任务主体已完成且已收口；必须位于 `done/`
- `archived`：任务只剩追溯价值；不得继续留在项目 live surface
- `abandoned`：任务终止；不得继续留在项目 live surface

## 4. archive 边界

- `archived` 与 `abandoned` 任务统一迁入：
- `.governance/archives/imported_projects/Get_wanted_food/project_governance/task_records/`
- 稳定吸收后的验收报告、阶段清单与旧执行记录，也优先迁到：
- `.governance/archives/imported_projects/Get_wanted_food/project_governance/`

## 5. 与 workspace work order 的关系

- `task_records/` 只承载项目内部轻量持续化，不替代 workspace `work_orders/`
- 若任务触碰 `.governance/`、loader、registry、project gate、工单生命周期、sync trigger matrix 或 cleanup / hygiene，必须升级或关联到 workspace `work_orders/`
- 正式执行事务的状态事实仍以 workspace `work_orders/<bucket>/.../TASK.yaml` 为准

## 6. 生命周期操作

- `planned | in_progress -> done`：使用项目自己的关闭脚本或等价流程
- `done -> archived`：使用项目自己的归档脚本或等价流程
- 目录与状态一致性检查：由项目自己的 task record hygiene 校验承担
