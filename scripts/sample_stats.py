#!/usr/bin/env python3
"""Compute sociodemographic statistics per cohort from xlsx/csv data.

Reads a YAML mapping that describes which columns hold age, gender,
school order/level/program, and which value defines each cohort.
Outputs a markdown summary table + per-cohort detail.

Example mapping (mapping.yaml):

    sources:
      - file: "Teachers.xlsx"
        sheet: "Form responses 1"
        cohort_column: 3
        cohorts:
          "in-service":
            match: "I currently teach."
            label: "In-service teachers"
          "pre-service":
            match: "PEF"
            label: "Pre-service teachers"
        variables:
          age: 4
          gender: 5
          order: 7
      - file: "Students.xlsx"
        sheet: "Form responses 1"
        cohort_column: 5
        cohorts:
          "univ":
            match_any: ["University - master's", "University - bachelor's"]
            label: "University students"
          "sec_ii":
            match: "Upper-secondary school"
            label: "Upper-secondary students"
        variables:
          age: 3
          gender: 4
          program: 7

Examples:
    sample_stats.py mapping.yaml --output sample-stats.md
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl not installed. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)


def load_rows(file: Path, sheet: str | None) -> list[list]:
    if file.suffix.lower() in (".xlsx", ".xlsm"):
        wb = openpyxl.load_workbook(file, data_only=True)
        ws = wb[sheet] if sheet else wb.active
        return [list(row) for row in ws.iter_rows(values_only=True)]
    if file.suffix.lower() == ".csv":
        import csv
        with file.open(newline="", encoding="utf-8") as f:
            return list(csv.reader(f))
    raise ValueError(f"Unsupported file format: {file.suffix}")


def match_cohort(value, spec: dict) -> bool:
    if value is None:
        return False
    s = str(value)
    if "match" in spec:
        return spec["match"] in s or s == spec["match"]
    if "match_any" in spec:
        return any(m in s for m in spec["match_any"])
    return False


def stats_age(values: list) -> dict:
    nums = [float(v) for v in values if isinstance(v, (int, float))]
    if not nums:
        return {"n": 0}
    nums.sort()
    n = len(nums)
    median = nums[n // 2] if n % 2 else (nums[n // 2 - 1] + nums[n // 2]) / 2
    return {
        "n": n,
        "min": int(min(nums)),
        "max": int(max(nums)),
        "mean": round(sum(nums) / n, 1),
        "median": round(median, 1),
    }


def gender_dist(values: list) -> dict:
    c = Counter(str(v).strip() if v else "non dichiarato" for v in values)
    total = len(values)
    out = {}
    for k, v in c.most_common():
        out[k] = (v, round(v / total * 100, 1) if total else 0.0)
    return out


def categorical_dist(values: list, top_n: int = 8) -> dict:
    c = Counter(
        str(v).strip().lower() if v else "non dichiarato"
        for v in values
    )
    total = sum(c.values())
    return {k: (v, round(v / total * 100, 1)) for k, v in c.most_common(top_n)}


def render_md(all_results: list[dict], mapping_path: Path) -> str:
    lines = [
        f"# Sample Statistics (auto)\n",
        f"- Mapping: `{mapping_path}`\n",
        f"- Cohorts: {len(all_results)}\n\n",
        "## Summary Table\n\n",
        "| Cohort | n | Age: mean (range) | Gender F / M / other-nd |\n",
        "|---|---|---|---|\n",
    ]
    for r in all_results:
        age = r["age"]
        age_str = f"{age['mean']} ({age['min']}–{age['max']})" if age["n"] else "n/a"
        g = r["gender"]
        f = next((p for k, p in g.items() if "femmin" in k.lower() or k == "F"), (0, 0))
        m = next((p for k, p in g.items() if "maschi" in k.lower() or k == "M"), (0, 0))
        other_total = sum(p[0] for k, p in g.items()
                          if "femmin" not in k.lower() and "maschi" not in k.lower() and k not in ("F", "M"))
        other_pct = round(other_total / r["n"] * 100, 1) if r["n"] else 0
        lines.append(f"| {r['label']} | {r['n']} | {age_str} | {f[1]}% / {m[1]}% / {other_pct}% |\n")

    lines.append("\n## By Cohort\n\n")
    for r in all_results:
        age = r["age"]
        lines.append(f"### {r['label']} (n={r['n']})\n\n")
        if age["n"]:
            lines.append(
                f"- **Age**: mean {age['mean']} years · range {age['min']}–{age['max']} · "
                f"median {age['median']}\n"
            )
        lines.append("- **Gender**: " + ", ".join(f"{k} {p[0]} ({p[1]}%)" for k, p in r["gender"].items()) + "\n")
        for var_name, dist in r["other_vars"].items():
            lines.append(f"- **{var_name.capitalize()}**: " + ", ".join(
                f"{k} {p[0]} ({p[1]}%)" for k, p in dist.items()
            ) + "\n")
        lines.append("\n")
    return "".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sample sociodemographic stats per cohort.")
    ap.add_argument("mapping", type=Path, help="YAML mapping file")
    ap.add_argument("--output", type=Path, default=None, help="Write markdown to this path")
    args = ap.parse_args()

    if not args.mapping.exists():
        print(f"ERROR: mapping not found: {args.mapping}", file=sys.stderr)
        return 2

    mapping = yaml.safe_load(args.mapping.read_text(encoding="utf-8"))
    base_dir = args.mapping.parent
    all_results: list[dict] = []

    for src in mapping.get("sources", []):
        file_path = (base_dir / src["file"]).resolve()
        rows = load_rows(file_path, src.get("sheet"))
        # skip header
        data_rows = rows[1:]
        cohort_col = src["cohort_column"] - 1
        for cohort_id, cohort_spec in src["cohorts"].items():
            matched = [r for r in data_rows if match_cohort(r[cohort_col], cohort_spec)]
            if not matched:
                continue
            ages_col = src["variables"].get("age")
            gender_col = src["variables"].get("gender")
            ages = [r[ages_col - 1] for r in matched] if ages_col else []
            genders = [r[gender_col - 1] for r in matched] if gender_col else []

            other_vars: dict[str, dict] = {}
            for vname, col_idx in src["variables"].items():
                if vname in ("age", "gender") or col_idx is None:
                    continue
                vals = [r[col_idx - 1] for r in matched]
                other_vars[vname] = categorical_dist(vals)

            all_results.append({
                "label": cohort_spec.get("label", cohort_id),
                "n": len(matched),
                "age": stats_age(ages),
                "gender": gender_dist(genders),
                "other_vars": other_vars,
            })

    md = render_md(all_results, args.mapping)
    if args.output:
        args.output.write_text(md, encoding="utf-8")
        print(f"Written: {args.output}", file=sys.stderr)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
