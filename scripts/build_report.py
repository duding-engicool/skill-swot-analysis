#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SWOT 分析报告生成器
读入结构化结果 JSON，生成 MD 文档 + 精美网页版 HTML。

用法：
  python build_report.py --input result.json --md-out report.md --html-out report.html
  python build_report.py --input result.json --html-out report.html        # 仅 HTML
  python build_report.py --input result.json --md-out report.md            # 仅 MD

输入 JSON 结构：
{
  "object": "品质部",
  "scope": "2026年",
  "focus": "质量提升",
  "strategy_text": "(可选) 上层战略文本",
  "quadrants": {
    "S": [{"text":"...", "note":""}],
    "W": [{"text":"...", "note":"供参考·待确认"}],
    "O": [{"text":"..."}],
    "T": [{"text":"..."}]
  },
  "strategies": {
    "SO": ["建议1", "建议2"],
    "WO": ["建议1"],
    "ST": ["建议1"],
    "WT": ["建议1"]
  },
  "priorities": [{"level":"P1","action":"...","reason":"..."}]
}
"""
import argparse
import json
import sys
import html
from datetime import datetime


def esc(s):
    return html.escape(str(s), quote=True)


def load_result(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_items(items):
    out = []
    for it in items or []:
        if isinstance(it, dict):
            txt = it.get("text", "")
            note = it.get("note", "")
            line = "• " + txt
            if note:
                line += f" 〔{note}〕"
            out.append(line)
        else:
            out.append("• " + str(it))
    if not out:
        out.append("• （未提供，影响对应战略组合）")
    return out


def build_md(r):
    L = []
    L.append(f"# SWOT 战略分析报告\n")
    L.append("## 一、分析概述\n")
    L.append(f"- 分析对象：{r.get('object','')}")
    L.append(f"- 分析范围：{r.get('scope','')}")
    L.append(f"- 特别关注：{r.get('focus','')}")
    st = r.get("strategy_text")
    if st:
        L.append(f"- 上层战略衔接：{st}")
    else:
        L.append("- 上层战略衔接：〔待提供战略后复核〕")
    L.append("")
    L.append("## 二、SWOT 四象限矩阵\n")
    q = r.get("quadrants", {})
    for key, label in [("S", "优势（S）"), ("W", "劣势（W）"),
                       ("O", "机会（O）"), ("T", "威胁（T）")]:
        L.append(f"### {label}\n")
        L.extend(list_items(q.get(key)))
        L.append("")
    L.append("## 三、战略组合建议\n")
    s = r.get("strategies", {})
    for key, label in [("SO", "SO 战略（进攻型）"), ("WO", "WO 战略（改善型）"),
                       ("ST", "ST 战略（防御型）"), ("WT", "WT 战略（生存型）")]:
        L.append(f"### {label}\n")
        L.extend(list_items(s.get(key)))
        L.append("")
    L.append("## 四、重点行动方向\n")
    for p in r.get("priorities", []) or []:
        L.append(f"- **{p.get('level','')}**：{p.get('action','')} — {p.get('reason','')}")
    L.append("")
    L.append(f"> 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(L)


CSS = """
:root{
  --s:#16a34a; --w:#dc2626; --o:#2563eb; --t:#ea580c;
  --bg:#f8fafc; --card:#ffffff; --ink:#1e293b; --muted:#64748b;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.7;padding:32px}
.wrap{max-width:1080px;margin:0 auto}
header{text-align:center;padding:28px 0 18px;border-bottom:3px solid #e2e8f0;margin-bottom:28px}
header h1{font-size:28px;letter-spacing:1px}
header .meta{color:var(--muted);font-size:14px;margin-top:10px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:32px}
.qcard{background:var(--card);border-radius:14px;padding:22px;box-shadow:0 4px 16px rgba(0,0,0,.06);
  border-top:5px solid #ccc}
.qcard.S{border-top-color:var(--s)} .qcard.W{border-top-color:var(--w)}
.qcard.O{border-top-color:var(--o)} .qcard.T{border-top-color:var(--t)}
.qcard h2{font-size:19px;margin-bottom:12px}
.qcard ul{list-style:none}
.qcard li{padding:7px 0;border-bottom:1px dashed #eee;font-size:15px}
.note{color:var(--t);font-size:12px;background:#fff7ed;padding:1px 6px;border-radius:4px;margin-left:4px}
.sec{background:var(--card);border-radius:14px;padding:24px;box-shadow:0 4px 16px rgba(0,0,0,.06);margin-bottom:28px}
.sec h2{font-size:21px;margin-bottom:16px;border-left:5px solid #334155;padding-left:12px}
.strat{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.scard{border-radius:10px;padding:16px;background:#f1f5f9}
.scard h3{font-size:16px;margin-bottom:8px}
.scard.SO{border-left:4px solid var(--s)} .scard.WO{border-left:4px solid var(--w)}
.scard.ST{border-left:4px solid var(--o)} .scard.WT{border-left:4px solid var(--t)}
.scard li{font-size:14px;margin:5px 0 5px 18px}
.prio{list-style:none}
.prio li{padding:10px 14px;margin:8px 0;border-radius:8px;background:#f1f5f9;font-size:15px}
.tag{display:inline-block;font-weight:700;color:#fff;border-radius:6px;padding:2px 9px;margin-right:8px;font-size:13px}
.tag.P1{background:var(--w)} .tag.P2{background:var(--o)} .tag.P3{background:var(--muted)}
footer{text-align:center;color:var(--muted);font-size:12px;margin-top:20px}
@media(max-width:720px){.grid,.strat{grid-template-columns:1fr}}
"""


def build_html(r):
    q = r.get("quadrants", {})
    s = r.get("strategies", {})

    def items_html(items):
        out = []
        for it in items or []:
            if isinstance(it, dict):
                txt = esc(it.get("text", ""))
                note = it.get("note", "")
                nt = f'<span class="note">{esc(note)}</span>' if note else ""
                out.append(f"<li>{txt}{nt}</li>")
            else:
                out.append(f"<li>{esc(it)}</li>")
        if not out:
            out.append('<li class="note">（未提供，影响对应战略组合）</li>')
        return "\n".join(out)

    def strat_html(items, cls):
        out = []
        for it in items or []:
            out.append(f"<li>{esc(it)}</li>")
        if not out:
            out.append('<li class="note">（对应象限缺失，无法生成）</li>')
        return "\n".join(out)

    prio_html = ""
    for p in r.get("priorities", []) or []:
        lvl = esc(p.get("level", ""))
        prio_html += (f'<li><span class="tag {lvl}">{lvl}</span>'
                      f'{esc(p.get("action",""))} — {esc(p.get("reason",""))}</li>')

    st = r.get("strategy_text")
    strat_line = esc(st) if st else "〔待提供战略后复核〕"

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SWOT 战略分析报告 · {esc(r.get('object',''))}</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<header>
  <h1>SWOT 战略分析报告</h1>
  <div class="meta">分析对象：{esc(r.get('object',''))} ｜ 范围：{esc(r.get('scope',''))} ｜ 关注：{esc(r.get('focus',''))}</div>
  <div class="meta">上层战略衔接：{strat_line}</div>
</header>

<section class="grid">
  <div class="qcard S"><h2>优势 Strengths</h2><ul>{items_html(q.get('S'))}</ul></div>
  <div class="qcard W"><h2>劣势 Weaknesses</h2><ul>{items_html(q.get('W'))}</ul></div>
  <div class="qcard O"><h2>机会 Opportunities</h2><ul>{items_html(q.get('O'))}</ul></div>
  <div class="qcard T"><h2>威胁 Threats</h2><ul>{items_html(q.get('T'))}</ul></div>
</section>

<section class="sec">
  <h2>战略组合建议</h2>
  <div class="strat">
    <div class="scard SO"><h3>SO 战略（进攻型）</h3><ul>{strat_html(s.get('SO'),'SO')}</ul></div>
    <div class="scard WO"><h3>WO 战略（改善型）</h3><ul>{strat_html(s.get('WO'),'WO')}</ul></div>
    <div class="scard ST"><h3>ST 战略（防御型）</h3><ul>{strat_html(s.get('ST'),'ST')}</ul></div>
    <div class="scard WT"><h3>WT 战略（生存型）</h3><ul>{strat_html(s.get('WT'),'WT')}</ul></div>
  </div>
</section>

<section class="sec">
  <h2>重点行动方向</h2>
  <ul class="prio">{prio_html}</ul>
</section>

<footer>本报告由 SWOT战略分析技能生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="SWOT 报告生成器")
    ap.add_argument("--input", required=True, help="结构化结果 JSON 路径")
    ap.add_argument("--md-out", help="输出 MD 路径")
    ap.add_argument("--html-out", help="输出 HTML 路径")
    args = ap.parse_args()

    try:
        r = load_result(args.input)
    except Exception as e:
        sys.stderr.write(f"读取输入失败：{e}\n")
        sys.exit(1)

    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8") as f:
            f.write(build_md(r))
        sys.stderr.write(f"MD 已生成：{args.md_out}\n")
    if args.html_out:
        with open(args.html_out, "w", encoding="utf-8") as f:
            f.write(build_html(r))
        sys.stderr.write(f"HTML 已生成：{args.html_out}\n")
    if not args.md_out and not args.html_out:
        sys.stderr.write("未指定 --md-out / --html-out，无输出。\n")


if __name__ == "__main__":
    main()
