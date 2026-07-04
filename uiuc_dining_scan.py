# -*- coding: utf-8 -*-
# 使用方法：uv run python uiuc_dining_scan.py --date 2026/04/23 --days 7 --output hits.csv

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional

from playwright.sync_api import sync_playwright


BASE_URL = "https://web.housing.illinois.edu/diningmenus"


def clean(s: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\u00a0", " ")).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the known-working UIUC dining JS scanner from Python."
    )
    parser.add_argument(
        "--date",
        required=False,
        default=None,
        help="起始日期，格式 YYYY/MM/DD；默认使用页面当前日期",
    )
    parser.add_argument("--days", type=int, default=7, help="扫描天数，默认 7")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--output", default=None, help="可选：保存 CSV 路径")
    return parser.parse_args()


def parse_start_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y/%m/%d")
    except ValueError:
        raise ValueError("date 必须使用 YYYY/MM/DD，例如 2026/04/27")
    return dt.strftime("%Y/%m/%d")


def extract_date_from_mealperiod(mealperiod: str) -> datetime:
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", mealperiod or "")
    if not m:
        return datetime(1970, 1, 1)
    mm, dd, yyyy = map(int, m.groups())
    return datetime(yyyy, mm, dd)


def save_csv(rows: List[Dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["restitle", "mealperiod", "item"])
        writer.writeheader()
        writer.writerows(rows)


def print_results(rows: List[Dict[str, str]]) -> None:
    if not rows:
        print("\n未找到 steak / salmon 相关菜品。")
        return

    w1 = max(len("restitle"), *(len(r["restitle"]) for r in rows))
    w2 = max(len("mealperiod"), *(len(r["mealperiod"]) for r in rows))
    w3 = max(len("item"), *(len(r["item"]) for r in rows))

    header = f"{'restitle'.ljust(w1)} | {'mealperiod'.ljust(w2)} | {'item'.ljust(w3)}"
    sep = "-" * len(header)

    print("\nResults:")
    print(sep)
    print(header)
    print(sep)
    for r in rows:
        print(
            f"{r['restitle'].ljust(w1)} | "
            f"{r['mealperiod'].ljust(w2)} | "
            f"{r['item'].ljust(w3)}"
        )
    print(sep)


JS_SCANNER_TEMPLATE = r"""
async ({ forcedStartDate, forcedDays }) => {
  const TARGETS = [
    { canonical: "Ikenberry Dining Center", aliases: ["Ikenberry Dining Center", "Ikenberry Dining Center (Ike)"] },
    { canonical: "ISR Dining Center", aliases: ["ISR Dining Center", "Illinois Street Dining Center", "Illinois Street Dining Center (ISR)"] },
    { canonical: "Kosher Kitchen", aliases: ["Kosher Kitchen"] },
    { canonical: "Lincoln/Allen Dining Hall", aliases: ["Lincoln/Allen Dining Hall", "Lincoln Avenue Dining Hall", "Lincoln Avenue Dining Hall (LAR)"] },
    { canonical: "PAR Dining Hall", aliases: ["PAR Dining Hall", "Pennsylvania Avenue Dining Hall", "Pennsylvania Avenue Dining Hall (PAR)"] }
  ];

  const KEY_RE = /\b(steak|salmon|rib|tip|cha|loin)\b/i;
  const BASE_URL = location.href.split("#")[0];

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const clean = (s) => (s || "").replace(/\u00a0/g, " ").replace(/\s+/g, " ").trim();

  async function waitFor(fn, { timeout = 20000, interval = 200, name = "condition" } = {}) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      try {
        const v = fn();
        if (v) return v;
      } catch {}
      await sleep(interval);
    }
    throw new Error(`Timeout waiting for ${name}`);
  }

  function isVisible(el, win = window) {
    if (!el) return false;
    const st = win.getComputedStyle(el);
    return st.display !== "none" && st.visibility !== "hidden";
  }

  function getControls(doc = document, win = window) {
    const dineop = doc.querySelector("#dineop");

    const inputs = [...doc.querySelectorAll("input")].filter(el => {
      const type = (el.type || "").toLowerCase();
      return isVisible(el, win) && !["hidden", "submit", "button", "checkbox", "radio"].includes(type);
    });

    const dateInput =
      inputs.find(el => /^\d{4}\/\d{2}\/\d{2}$/.test(clean(el.value))) ||
      inputs.find(el => /^\d{2}\/\d{2}\/\d{4}$/.test(clean(el.value))) ||
      inputs.find(el => /date|serv/i.test(`${el.id} ${el.name} ${el.className} ${el.placeholder}`)) ||
      inputs[0] ||
      null;

    const viewBtn =
      [...doc.querySelectorAll("button,input[type='submit'],input[type='button'],a")]
        .find(el => /^view$/i.test(clean(el.textContent || el.value)));

    return { dineop, dateInput, viewBtn };
  }

  function parseDateLike(s) {
    const v = clean(s);
    if (/^\d{4}\/\d{2}\/\d{2}$/.test(v)) {
      const [y, m, d] = v.split("/").map(Number);
      return { y, m, d, fmt: "yyyy/mm/dd" };
    }
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(v)) {
      const [m, d, y] = v.split("/").map(Number);
      return { y, m, d, fmt: "mm/dd/yyyy" };
    }
    return null;
  }

  function addDays(parts, n) {
    const dt = new Date(parts.y, parts.m - 1, parts.d + n);
    return { y: dt.getFullYear(), m: dt.getMonth() + 1, d: dt.getDate() };
  }

  function formatDate(parts, fmt) {
    const y = String(parts.y);
    const m = String(parts.m).padStart(2, "0");
    const d = String(parts.d).padStart(2, "0");
    if (fmt === "mm/dd/yyyy") return `${m}/${d}/${y}`;
    if (fmt === "yyyy-mm-dd") return `${y}-${m}-${d}`;
    return `${y}/${m}/${d}`;
  }

  function formatDateForMealperiod(parts) {
    const m = String(parts.m).padStart(2, "0");
    const d = String(parts.d).padStart(2, "0");
    const y = String(parts.y);
    return `${m}/${d}/${y}`;
  }

  function setSelectValue(selectEl, value, popupWin) {
    selectEl.value = value;
    selectEl.dispatchEvent(new popupWin.Event("input", { bubbles: true }));
    selectEl.dispatchEvent(new popupWin.Event("change", { bubbles: true }));
  }

  function setDateValue(inputEl, dateStr, popupWin) {
    const type = (inputEl.type || "").toLowerCase();
    if (type === "date") {
      const p = parseDateLike(dateStr);
      inputEl.value = `${p.y}-${String(p.m).padStart(2, "0")}-${String(p.d).padStart(2, "0")}`;
    } else {
      inputEl.value = dateStr;
    }
    inputEl.dispatchEvent(new popupWin.Event("input", { bubbles: true }));
    inputEl.dispatchEvent(new popupWin.Event("change", { bubbles: true }));
  }

  function getTargetOption(selectEl, target) {
    const options = [...selectEl.options].map(o => ({
      value: o.value,
      text: clean(o.textContent)
    }));

    for (const alias of target.aliases) {
      const exact = options.find(o => o.text === alias);
      if (exact) return exact;
    }

    for (const alias of target.aliases) {
      const fuzzy = options.find(o => o.text.includes(alias) || alias.includes(o.text));
      if (fuzzy) return fuzzy;
    }

    return null;
  }

  async function waitPopupLoad(popup, timeout = 20000) {
    await waitFor(() => {
      if (!popup || popup.closed) throw new Error("popup closed");
      try {
        return popup.document && popup.document.readyState === "complete";
      } catch {
        return false;
      }
    }, { timeout, name: "popup load" });
  }

  async function openRestaurantContext(popup, optionValue) {
    popup.location.href = BASE_URL;
    await waitPopupLoad(popup);
    await sleep(500);

    const controls = await waitFor(() => {
      const c = getControls(popup.document, popup);
      return c.dineop && c.viewBtn ? c : null;
    }, { name: "restaurant controls" });

    setSelectValue(controls.dineop, optionValue, popup);
    await sleep(200);
    controls.viewBtn.click();

    await waitPopupLoad(popup);
    await waitFor(() => popup.document.querySelector("#menuData"), { name: "#menuData after restaurant view" });
    await sleep(600);
  }

  async function setDateAndReload(popup, dateStr, targetMealDate) {
    const controls = await waitFor(() => {
      const c = getControls(popup.document, popup);
      return c.dateInput && c.viewBtn ? c : null;
    }, { name: "date controls" });

    setDateValue(controls.dateInput, dateStr, popup);
    await sleep(150);
    controls.viewBtn.click();

    await waitPopupLoad(popup);
    await waitFor(() => popup.document.querySelector("#menuData"), { name: "#menuData after date view" });

    const menuText = clean(popup.document.querySelector("#menuData")?.innerText || "");
    if (menuText.includes("No Data To Display")) {
      return { status: "no_menu" };
    }

    await waitFor(() => {
      return [...popup.document.querySelectorAll("#menuData h4.mealperiod")]
        .some(h4 => clean(h4.textContent).includes(targetMealDate));
    }, { timeout: 15000, interval: 200, name: `mealperiod ${targetMealDate}` });

    await sleep(400);
    return { status: "ok" };
  }

  function splitItems(s) {
    return clean(s)
      .split(/\s*,\s*/)
      .map(clean)
      .filter(Boolean);
  }

  function extractMatches(doc, fallbackTitle = "") {
    const restitle = clean(doc.querySelector("#resTitle")?.textContent) || fallbackTitle;
    const blocks = [...doc.querySelectorAll("#menuData h4.mealperiod, #menuData p.course")];

    let currentMealperiod = "";
    const out = [];
    const seen = new Set();

    for (const node of blocks) {
      if (node.matches("h4.mealperiod")) {
        currentMealperiod = clean(node.textContent);
        continue;
      }

      if (node.matches("p.course")) {
        if (!currentMealperiod) continue;

        const cloned = node.cloneNode(true);
        cloned.querySelectorAll("b").forEach(b => b.remove());
        const trailing = clean(cloned.textContent);
        if (!trailing) continue;

        const items = splitItems(trailing);
        for (const item of items) {
          if (KEY_RE.test(item)) {
            const key = `${restitle}||${currentMealperiod}||${item}`;
            if (!seen.has(key)) {
              seen.add(key);
              out.push({
                restitle,
                mealperiod: currentMealperiod,
                item
              });
            }
          }
        }
      }
    }

    return out;
  }

  function extractDateFromMealperiod(mealperiod) {
    const m = String(mealperiod || "").match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
    if (!m) return new Date(0);
    const [, mm, dd, yyyy] = m;
    return new Date(Number(yyyy), Number(mm) - 1, Number(dd));
  }

  const main = getControls(document, window);
  if (!main.dineop || !main.viewBtn) {
    throw new Error("当前页没识别到 #dineop 或 View 按钮。");
  }

  let start = null;
  if (forcedStartDate) {
    start = parseDateLike(forcedStartDate);
    if (!start) throw new Error(`forcedStartDate 无法解析: ${forcedStartDate}`);
  } else if (main.dateInput && clean(main.dateInput.value)) {
    start = parseDateLike(main.dateInput.value);
  }

  if (!start) {
    const now = new Date();
    start = { y: now.getFullYear(), m: now.getMonth() + 1, d: now.getDate(), fmt: "yyyy/mm/dd" };
  }

  const resolvedTargets = [];
  for (const t of TARGETS) {
    const option = getTargetOption(main.dineop, t);
    if (option) {
      resolvedTargets.push({
        canonical: t.canonical,
        optionValue: option.value,
        optionText: option.text
      });
    } else {
      console.warn(`没在下拉框里找到餐厅：${t.canonical}`);
    }
  }

  console.log("Resolved restaurants:", resolvedTargets);

  const popup = window.open(BASE_URL, "uiuc_menu_scan_popup", "width=1300,height=900");
  if (!popup) {
    throw new Error("弹窗被拦截了。先允许此站点弹窗，再重跑。");
  }

  await waitPopupLoad(popup);
  await sleep(400);

  const detailed = [];
  const failures = [];
  const noMenus = [];

  for (const target of resolvedTargets) {
    try {
      await openRestaurantContext(popup, target.optionValue);

      for (let i = 0; i < forcedDays; i++) {
        const day = addDays(start, i);
        const inputDate = formatDate(day, start.fmt || "yyyy/mm/dd");
        const mealperiodDate = formatDateForMealperiod(day);

        try {
          const state = await setDateAndReload(popup, inputDate, mealperiodDate);

          if (state.status === "no_menu") {
            noMenus.push({
              restaurant: target.canonical,
              date: mealperiodDate,
              reason: "No Data To Display"
            });
            console.warn(`无菜单数据: ${target.canonical} | ${mealperiodDate}`);
            continue;
          }

          const rows = extractMatches(popup.document, target.canonical);
          detailed.push(...rows);
          console.log(`扫完: ${target.canonical} | ${mealperiodDate} | 命中 ${rows.length}`);
        } catch (err) {
          failures.push({
            restaurant: target.canonical,
            date: mealperiodDate,
            error: String(err)
          });
          console.warn("日期扫描失败:", target.canonical, mealperiodDate, err);
        }
      }
    } catch (err) {
      failures.push({
        restaurant: target.canonical,
        date: "(context)",
        error: String(err)
      });
      console.warn("餐厅上下文失败:", target.canonical, err);
    }
  }

  const dedupMap = new Map();
  for (const row of detailed) {
    const k = `${row.restitle}||${row.mealperiod}||${row.item}`;
    dedupMap.set(k, row);
  }

  const finalRows = [...dedupMap.values()].sort((a, b) =>
    extractDateFromMealperiod(a.mealperiod) - extractDateFromMealperiod(b.mealperiod) ||
    a.restitle.localeCompare(b.restitle) ||
    a.mealperiod.localeCompare(b.mealperiod) ||
    a.item.localeCompare(b.item)
  );

  window.__uiuc_hits = finalRows;
  window.__uiuc_failures = failures;
  window.__uiuc_no_menus = noMenus;

  return {
    hits: finalRows,
    failures,
    noMenus,
    resolvedTargets
  };
}
"""


def main() -> int:
    args = parse_args()
    start_date = parse_start_date(args.date)
    forced_start = start_date if start_date else None
    forced_days = max(1, int(args.days))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context()
        page = context.new_page()

        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(1200)

        result = page.evaluate(
            JS_SCANNER_TEMPLATE,
            {
                "forcedStartDate": forced_start,
                "forcedDays": forced_days,
            },
        )

        browser.close()

    rows = [
        {
            "restitle": clean(r.get("restitle")),
            "mealperiod": clean(r.get("mealperiod")),
            "item": clean(r.get("item")),
        }
        for r in result.get("hits", [])
        if clean(r.get("item"))
    ]

    rows.sort(
        key=lambda r: (
            extract_date_from_mealperiod(r["mealperiod"]),
            r["restitle"],
            r["mealperiod"],
            r["item"],
        )
    )

    print("Resolved restaurants:")
    for t in result.get("resolvedTargets", []):
        print(f"  - {t['canonical']}  <=  {t['optionText']}")

    print_results(rows)

    if args.output:
        save_csv(rows, args.output)
        print(f"\nCSV 已保存到: {args.output}")

    no_menus = result.get("noMenus", [])
    if no_menus:
        print("\nNo-menu / no-data cases:")
        print(json.dumps(no_menus, ensure_ascii=False, indent=2))

    failures = result.get("failures", [])
    if failures:
        print("\nFailures:")
        print(json.dumps(failures, ensure_ascii=False, indent=2))
        raise RuntimeError("scan incomplete: failures detected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
