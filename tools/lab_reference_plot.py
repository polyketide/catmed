#!/usr/bin/env python3
"""Plot lab results against their reference ranges — radar + position bars.

Standard-library only, so it runs anywhere Python does. Reads a long-format CSV
of lab values (one row per analyte per date, each carrying its own reference
range) and renders a self-contained HTML page with two views:

  1. A multi-system radar: how far each physiological system sits OUTSIDE its
     reference range, with several dates overlaid so a pattern's change is
     visible at a glance.
  2. Reference-range position bars: one bar per analyte showing the normal zone
     and where each date's value falls, so direction and in-range movement are
     legible per analyte.

What this tool refuses to do, on purpose
----------------------------------------
- **It does not emit a single "health score."** Different systems are not
  commensurable; summing or averaging their deviations manufactures a
  precise-looking number that means nothing. There is no total.
- **Radar radius is not clinical severity.** The radius is distance outside the
  reference interval measured in reference-widths. An analyte with a wide
  reference (e.g. haematocrit 30–52) barely moves the radius even when out of
  range, while an acute-phase protein spikes it. Read the annotated values, not
  the polygon area.
- **Missing is not normal.** A date that did not measure an analyte is drawn as
  a gap, never as an in-range point.

It is a visualiser of what the report already says, not a diagnosis and not a
validated instrument. Validated feline illness-severity scores exist (e.g. the
APPLE score) but require clinical inputs beyond biochemistry; this is not a
substitute for one, and every reading belongs with the attending clinician.

Privacy: this tool ships with no data. Point it at a CSV that lives outside the
repository; patient data must never be committed here.

CSV columns (header required): date,analyte,value,lo,hi

    python3 lab_reference_plot.py labs.csv --html out.html --title "Feline panel"
    python3 lab_reference_plot.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import html
import math
import sys
import tempfile
from pathlib import Path
from typing import Optional

# System -> (analytes folded into it, a note on which direction is meaningful).
# The radius folds a system to its single most out-of-range analyte (max), which
# is then named in the annotation table, rather than averaging abnormal with
# normal and hiding the signal.
DOMAINS = {
    "Anaemia / RBC": (["HCT", "HGB"], "low is meaningful"),
    "Inflammation": (["NEUT", "WBC", "MONO", "FIB"], "high is meaningful"),
    "Liver enzymes": (["AST", "ALT", "GGT"], "high is meaningful"),
    "Kidney": (["CRE", "BUN"], "high renal; low CRE = muscle loss"),
    "Protein / nutrition": (["ALB", "TCHO", "TP"], "low is meaningful"),
    "Electrolytes": (["K", "Na", "Cl", "Ca"], "either direction matters"),
    "Glucose / metabolic": (["GLU"], "high often stress (may be benign)"),
}
# Analytes not measured on every date: reported separately, kept out of the
# comparable radar axes so a one-off reading cannot distort the shape.
ONE_OFF = {"FIB", "APTT", "PT"}
RMAX = 2.0                          # radius cap, in reference-widths
COLORS = ["#3b6ea5", "#c9820a", "#c0392b", "#2e8b57", "#7d3c98"]


def load(path: Path):
    """CSV -> ({date: {analyte: (value, lo, hi)}}, ordered date list)."""
    data: dict[str, dict] = {}
    order: list[str] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            d = (row.get("date") or "").strip()
            a = (row.get("analyte") or "").strip()
            if not d or not a:
                continue
            if d not in data:
                data[d] = {}
                order.append(d)
            try:
                data[d][a] = (float(row["value"]), float(row["lo"]), float(row["hi"]))
            except (ValueError, KeyError, TypeError):
                continue
    return data, order


def deviation(v: float, lo: float, hi: float) -> float:
    """Distance outside the reference interval, in reference-widths. In-range = 0."""
    w = hi - lo
    if w <= 0:
        return 0.0
    if v < lo:
        return (lo - v) / w
    if v > hi:
        return (v - hi) / w
    return 0.0


def domain_dev(labs: dict, analytes: list[str]) -> tuple[float, Optional[str]]:
    """A system's deviation = its most out-of-range analyte; returns the driver."""
    best, driver = 0.0, None
    for a in analytes:
        if a in labs:
            dv = deviation(*labs[a])
            if dv > best:
                best, driver = dv, a
    return best, driver


def _fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def radar_svg(data, order, size: int = 520) -> str:
    cx = cy = size / 2
    R = size / 2 - 96
    labels = list(DOMAINS)
    n = len(labels)
    ang = [-math.pi / 2 + 2 * math.pi * i / n for i in range(n)]
    p = [f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" '
         f'font-family="system-ui,sans-serif" font-size="11">']
    for ring in (0.5, 1.0, 1.5, 2.0):
        rr = R * ring / RMAX
        poly = " ".join(f"{cx+rr*math.cos(a):.1f},{cy+rr*math.sin(a):.1f}" for a in ang)
        p.append(f'<polygon points="{poly}" fill="none" stroke="var(--grid)" stroke-width="0.7"/>')
        p.append(f'<text x="{cx+3}" y="{cy-rr:.1f}" fill="var(--muted)" font-size="9">{ring}</text>')
    for i, lab in enumerate(labels):
        x2, y2 = cx + R * math.cos(ang[i]), cy + R * math.sin(ang[i])
        p.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="var(--grid)" stroke-width="0.7"/>')
        lx, ly = cx + (R + 16) * math.cos(ang[i]), cy + (R + 16) * math.sin(ang[i])
        anchor = "middle" if abs(math.cos(ang[i])) < 0.3 else ("start" if math.cos(ang[i]) > 0 else "end")
        p.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="var(--ink)" '
                 f'font-weight="600">{html.escape(lab)}</text>')
    for di, date in enumerate(order):
        pts = []
        for i, lab in enumerate(labels):
            dev, _ = domain_dev(data[date], DOMAINS[lab][0])
            r = R * min(dev, RMAX) / RMAX
            pts.append((cx + r * math.cos(ang[i]), cy + r * math.sin(ang[i])))
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        c = COLORS[di % len(COLORS)]
        p.append(f'<polygon points="{poly}" fill="{c}" fill-opacity="0.10" stroke="{c}" stroke-width="1.8"/>')
        for x, y in pts:
            p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="{c}"/>')
    p.append("</svg>")
    return "".join(p)


def annotation_rows(data, order) -> str:
    rows = []
    for lab, (analytes, note) in DOMAINS.items():
        cells = []
        for date in order:
            dev, driver = domain_dev(data[date], analytes)
            if driver and dev > 0:
                v, lo, hi = data[date][driver]
                dirn = "&darr;" if v < lo else ("&uarr;" if v > hi else "")
                cell = f"{dev:.2f}<br><span class='drv'>{html.escape(driver)} {_fmt(v)}{dirn}</span>"
            else:
                cell = "0" if driver else "<span class='drv'>&mdash;</span>"
            cells.append(f"<td>{cell}</td>")
        rows.append(f"<tr><th>{html.escape(lab)}<br><span class='drv'>{html.escape(note)}</span>"
                    f"</th>{''.join(cells)}</tr>")
    return "".join(rows)


def one_off_note(data, order) -> str:
    lines = []
    for a in sorted(ONE_OFF):
        hits = [(d, data[d][a]) for d in order if a in data[d]]
        if hits:
            parts = []
            for d, (v, lo, hi) in hits:
                dirn = "&darr;" if v < lo else ("&uarr;" if v > hi else "")
                parts.append(f"{html.escape(d)}: {_fmt(v)}{dirn} (dev {deviation(v, lo, hi):.2f})")
            lines.append(f"<b>{html.escape(a)}</b> measured on some dates only: " + "; ".join(parts))
    return "<br>".join(lines) or "none"


def position_bars(data, order) -> str:
    groups = []
    for lab, (analytes, _note) in DOMAINS.items():
        rows = []
        for a in analytes:
            ref = next((data[d][a] for d in order if a in data[d]), None)
            if ref is None:
                continue
            _, lo, hi = ref
            span = (hi - lo) if hi > lo else 1.0
            pad = span * 0.6
            left, width = lo - pad, (hi + pad) - (lo - pad)
            zleft = (lo - left) / width * 100
            zwid = (hi - lo) / width * 100
            dots, latest = [], None
            for di, d in enumerate(order):
                if a not in data[d]:
                    continue
                v = data[d][a][0]
                pct = max(0.0, min(100.0, (v - left) / width * 100))
                out = v < lo or v > hi
                r = 6 if d == order[-1] else 4
                dots.append(f'<span class="pdot" style="left:{pct:.1f}%;width:{r*2}px;height:{r*2}px;'
                            f'background:{COLORS[di%len(COLORS)]};'
                            f'{"box-shadow:0 0 0 2px var(--warn)" if out else ""}"></span>')
                dirn = "&darr;" if v < lo else ("&uarr;" if v > hi else "")
                latest = (v, dirn, out)
            vtxt = f"{_fmt(latest[0])}{latest[1]}" if latest else "&mdash;"
            vcls = "vout" if latest and latest[2] else "vin"
            rows.append(
                f'<div class="brow"><span class="bname">{html.escape(a)}</span>'
                f'<span class="btrack"><span class="bzone" style="left:{zleft:.1f}%;width:{zwid:.1f}%"></span>'
                f'{"".join(dots)}</span>'
                f'<span class="bval {vcls}">{vtxt}</span>'
                f'<span class="bref">{_fmt(lo)}&ndash;{_fmt(hi)}</span></div>')
        if rows:
            groups.append(f'<div class="bgroup"><div class="bghead">{html.escape(lab)}</div>{"".join(rows)}</div>')
    return "".join(groups)


def render_html(data, order, out: Path, title: str = "Lab panel") -> None:
    legend = " ".join(
        f'<span class="lg"><span class="dot" style="background:{COLORS[i%len(COLORS)]}"></span>'
        f'{html.escape(d)}</span>' for i, d in enumerate(order))
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>
:root{{--bg:#faf9f7;--panel:#fff;--ink:#1a1a1a;--muted:#8a8a8a;--grid:#d9d5cd;--drv:#b5651d;--warn:#c0392b;--zone:#c9ead0}}
@media(prefers-color-scheme:dark){{:root{{--bg:#16151a;--panel:#20202a;--ink:#eee;--muted:#999;--grid:#3a3a45;--drv:#d8975a;--warn:#e06a6a;--zone:#2b4a35}}}}
body{{background:var(--bg);color:var(--ink);font-family:system-ui,sans-serif;max-width:740px;margin:0 auto;padding:24px 16px}}
h1{{font-size:20px;margin:0 0 4px}}.sub{{color:var(--muted);font-size:13px;margin:0 0 14px}}
.card{{background:var(--panel);border:1px solid var(--grid);border-radius:10px;padding:14px;margin:12px 0}}
.warn{{border-left:4px solid var(--warn)}}
.lg{{margin-right:14px;font-size:12px}}.dot{{display:inline-block;width:11px;height:11px;border-radius:50%;vertical-align:middle;margin-right:4px}}
svg{{display:block;margin:0 auto;max-width:100%}}
table{{width:100%;border-collapse:collapse;font-size:12px;margin-top:6px}}
th,td{{border:1px solid var(--grid);padding:5px 7px;text-align:center;vertical-align:top}}
th:first-child{{text-align:left;width:34%}}.drv{{color:var(--drv);font-size:10.5px;font-weight:400}}
.note{{color:var(--muted);font-size:11.5px;line-height:1.7;margin:6px 2px}}
.bgroup{{margin:10px 0}}.bghead{{font-weight:600;font-size:12px;margin:8px 0 4px}}
.brow{{display:flex;align-items:center;gap:8px;margin:3px 0;font-size:11.5px}}
.bname{{width:54px;flex:none;text-align:right;color:var(--muted)}}
.btrack{{position:relative;flex:1;height:14px;background:var(--grid);border-radius:7px}}
.bzone{{position:absolute;top:0;height:14px;background:var(--zone);border-radius:7px}}
.pdot{{position:absolute;top:50%;transform:translate(-50%,-50%);border-radius:50%}}
.bval{{width:52px;flex:none;font-variant-numeric:tabular-nums}}.vin{{color:var(--ink)}}.vout{{color:var(--warn);font-weight:700}}
.bref{{width:82px;flex:none;color:var(--muted);font-size:10px}}
</style></head><body>
<h1>{html.escape(title)}</h1>
<p class="sub">{html.escape(order[0])} &rarr; {html.escape(order[-1])} &middot; deviation from reference (in reference-widths), dates overlaid</p>
<div class="card"><div style="margin-bottom:6px">{legend}</div>{radar_svg(data, order)}</div>
<div class="card warn"><p class="note"><b>&#9888; This is a deviation map, not a health score.</b>
Radius is not clinical severity: a wide-reference analyte (HCT) barely moves it even when out of range,
while an acute-phase protein spikes it. <b>Read the values in the table below</b>, not the polygon area.
Systems are not commensurable, so there is <b>no total score</b>. Every reading belongs with the attending
clinician; validated feline severity scores (e.g. APPLE) need clinical inputs beyond biochemistry.</p></div>
<div class="card"><table><tr><th>System / direction</th>{''.join(f'<td><b>{html.escape(d)}</b></td>' for d in order)}</tr>
{annotation_rows(data, order)}</table>
<p class="note">Number = the system's most out-of-range analyte (0 = all in range); orange = the driving analyte and its value.</p>
<p class="note">&#128204; One-off analytes (not on every date, kept out of the radar axes): {one_off_note(data, order)}</p></div>
<div class="card"><div style="font-weight:600;margin-bottom:2px">Reference-range position bars</div>
<p class="note">One bar per analyte: <span style="color:var(--zone)">&#9632;</span> green = normal zone; dots = each date
(latest larger, red ring = out of range). Shows <b>direction and in-range movement</b> the radar cannot.</p>
<div style="margin-bottom:6px">{legend}</div>{position_bars(data, order)}</div>
</body></html>"""
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out.name}")


def terminal(data, order) -> None:
    print(f"\nMulti-system deviation ({order[0]} -> {order[-1]})  "
          f"[value = reference-widths outside range, 0 = in range]\n")
    print("  system".ljust(22) + "".join(d.rjust(11) for d in order))
    for lab, (analytes, _n) in DOMAINS.items():
        cells = []
        for date in order:
            dev, driver = domain_dev(data[date], analytes)
            cells.append((f"{dev:.2f}" + (f"({driver})" if driver else "")).rjust(11))
        print(f"  {lab}".ljust(22) + "".join(cells))
    print("\n  ! radius is not severity; no total (systems not commensurable).\n")


def self_test() -> int:
    """Prove the arithmetic and that a page renders, without any patient data."""
    # deviation: in-range = 0, below and above are symmetric in reference-widths
    assert deviation(35, 30, 50) == 0.0
    assert abs(deviation(28, 30, 50) - 0.1) < 1e-9      # 2 below / width 20
    assert abs(deviation(60, 30, 50) - 0.5) < 1e-9      # 10 above / width 20
    assert deviation(5, 5, 5) == 0.0                    # zero-width guard
    # domain_dev folds to the worst analyte and names it
    labs = {"HCT": (28.0, 30.0, 50.0), "HGB": (11.0, 9.0, 16.0)}
    dev, driver = domain_dev(labs, ["HCT", "HGB"])
    assert driver == "HCT" and abs(dev - 0.1) < 1e-9
    # render a synthetic two-date page and check the honest markers are present
    data = {"D1": {"HCT": (35.0, 30.0, 50.0), "AST": (40.0, 18.0, 51.0)},
            "D2": {"HCT": (28.0, 30.0, 50.0), "AST": (77.0, 18.0, 51.0)}}
    order = ["D1", "D2"]
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "t.html"
        render_html(data, order, out, title="self-test")
        page = out.read_text(encoding="utf-8")
    assert "not a health score" in page
    assert "no total score" in page
    assert "position bars" in page.lower()
    assert "vout" in page            # HCT 28 on D2 is flagged out-of-range
    print("SELF_TEST: PASS")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Plot lab results against reference ranges (stdlib only)")
    ap.add_argument("csv", nargs="?", type=Path)
    ap.add_argument("--html", type=Path)
    ap.add_argument("--title", default="Lab panel")
    ap.add_argument("--self-test", action="store_true", help="run internal checks and exit")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.csv or not args.csv.exists():
        print("need a CSV (columns: date,analyte,value,lo,hi), or --self-test", file=sys.stderr)
        return 1
    data, order = load(args.csv)
    if not order:
        print("no data rows", file=sys.stderr)
        return 1
    terminal(data, order)
    if args.html:
        render_html(data, order, args.html, title=args.title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
