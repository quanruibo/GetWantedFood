# CLI

- 主脚本：`../uiuc_dining_scan.py`
- 当前用途：扫描 UIUC dining menus，筛出想找的菜品并按餐厅 / meal period 输出

## 参数

- `--date YYYY/MM/DD`：可选起始日期；未提供时使用页面当前日期
- `--days N`：扫描天数，默认 `7`
- `--headed`：以有头浏览器运行
- `--output <path>`：可选 CSV 输出路径

## 输出

- 标准输出：命中的餐厅 / meal period / item 表格
- 可选 CSV：字段为 `restitle`、`mealperiod`、`item`
- 若扫描存在失败项，脚本会打印 failure 列表并以非零状态退出
