"""DECISIONS.md and REPORT.md: read, save and generate as real files at the repository root."""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import sqlite3
from pathlib import Path

from backend.db import metadata, rows

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
REPORT = ROOT / "REPORT.md"
MAX_BYTES = 256 * 1024


class Conflict(RuntimeError):
    pass


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write(path: Path, text: str) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def read_decisions() -> dict:
    text = DECISIONS.read_text(encoding="utf-8") if DECISIONS.exists() else ""
    return {"path": str(DECISIONS), "content": text, "digest": _digest(text)}


def save_decisions(content: str, base_digest: str | None) -> dict:
    current = read_decisions()
    if base_digest and base_digest != current["digest"]:
        raise Conflict("DECISIONS.md changed on disk since you loaded it. Reload before saving.")
    _write(DECISIONS, content if content.endswith("\n") else content + "\n")
    return read_decisions()


def report_status(conn: sqlite3.Connection) -> dict:
    md = metadata(conn)
    complete = md.get("analysis_status") == "complete"
    text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    return {
        "path": str(REPORT),
        "analysis_complete": complete,
        "data_source": md.get("data_source"),
        "message": None if complete else (
            "Analysis not ready: the app is on mock data and the synthetic dataset has not been analysed. "
            "Generating now produces a clearly labelled DEMO report with no findings."),
        "content": text,
    }


NA = "_Not available yet._"


def _section(build) -> list[str]:
    """Render one report section; any missing data becomes 'Not available yet' instead of an error."""
    try:
        out = build()
        return out if out else [NA]
    except Exception:  # missing table/column/value: degrade, never fail the whole report
        return [NA]


def generate_report(conn: sqlite3.Connection) -> dict:
    md = metadata(conn)
    mock = md.get("data_source") != "assignment" or md.get("analysis_status") != "complete"
    cur = md.get("currency", "USD")
    k = {r["kpi_id"]: r["value"] for r in rows(conn, "SELECT kpi_id, value FROM kpi")}
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tag = "(SYNTHETIC/DEMO) " if mock else ""

    def memo():
        return [f"- {tag}Revenue changed {k['revenue_change_pct']:+.1f}% from Q2 ({cur} {k['revenue_q2']:,.0f}) "
                f"to Q3 ({cur} {k['revenue_q3']:,.0f}).",
                f"- {tag}Sign-ups changed {k['signup_growth_pct']:+.1f}%; recomputed 30-day retention "
                f"{k['retention30_q2_independent']:.1%} -> {k['retention30_q3_independent']:.1%}.",
                "- Recommendations: not available yet (no analysis has been run)."]

    def bridge():
        items = rows(conn, "SELECT cause, central_pp, low_pp, high_pp, confidence FROM bridge_item ORDER BY position")
        return (["| Cause | Central (pp) | Low | High | Confidence |", "|---|---|---|---|---|"]
                + [f"| {b['cause']} | {b['central_pp']:+.2f} | {b['low_pp']:+.2f} | {b['high_pp']:+.2f} | "
                   f"{'n/a (demo)' if mock else b['confidence']} |" for b in items]
                + [f"| **Total** | **{k['revenue_change_pct']:+.2f}** | | | |"])

    def initiatives():
        out = []
        for i in rows(conn, "SELECT initiative_id, name, recommendation FROM initiative"):
            out += [f"### {i['name']}", f"- Recommendation: **{i['recommendation']}**"]
            if i["initiative_id"] == "onboarding":
                out += [f"- {tag}{m['label']}: effect {m['effect'] * (100 if m['unit'] == 'rate' else 1):+.2f}"
                        f"{' pp' if m['unit'] == 'rate' else ''} (95% CI {m['ci_low'] * (100 if m['unit'] == 'rate' else 1):+.2f}"
                        f" to {m['ci_high'] * (100 if m['unit'] == 'rate' else 1):+.2f})"
                        for m in rows(conn, "SELECT * FROM experiment_metric ORDER BY position")]
            elif i["initiative_id"] == "referral":
                out += [f"- {tag}{f['stage']}: {f['count']:,}"
                        for f in rows(conn, "SELECT stage, count FROM referral_funnel ORDER BY position")]
            out += [f"- {tag}{m['label']}: " + ("not available yet" if m["value"] is None else f"{m['value']:,.4g}")
                    for m in rows(conn, "SELECT label, value FROM initiative_metric WHERE initiative_id = ? "
                                        "ORDER BY position", (i["initiative_id"],))]
            out.append("")
        return out

    lines = ["**Reproduce:** not available yet (the analysis pipeline has not been written).", ""]
    if mock:
        lines += [f"> **SYNTHETIC/DEMO REPORT - generated {now} from mock development data.** Every number is "
                  "synthetic and is not a finding. The assignment analysis is not complete.", ""]
    lines += ["## 1. Memo to the CEO", "", *_section(memo), "",
              "## 2. Revenue bridge", "", *_section(bridge), "",
              "## 3. Evidence for each initiative", "", *_section(initiatives), "",
              "## 4. What the agent got wrong", "", NA, "",
              "## 5. Not done and not known", "",
              "- Not available yet: the synthetic dataset (data/) has been generated but not analysed.",
              "- UNDERSTANDING.md is a draft awaiting review.", ""]
    _write(REPORT, "\n".join(lines))
    status = report_status(conn)
    status.update(saved=True, bytes=REPORT.stat().st_size, generated_at=now)
    return status
