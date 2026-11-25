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


def generate_report(conn: sqlite3.Connection) -> dict:
    md = metadata(conn)
    if md.get("analysis_status") == "complete":
        raise NotImplementedError("Final report rendering is written together with the analysis.")
    k = {r["kpi_id"]: r for r in rows(conn, "SELECT kpi_id, label, value, unit FROM kpi")}
    bridge = rows(conn, "SELECT cause, central_pp, low_pp, high_pp FROM bridge_item ORDER BY position")
    inits = rows(conn, "SELECT name, recommendation FROM initiative")
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    not_ready = "_Not available: the analysis has not been run. No finding is stated here._"
    lines = [
        "**Reproduce:** `not available yet - the analysis pipeline has not been written`",
        "",
        "> **DEMO REPORT - NOT THE ASSIGNMENT REPORT.** Generated from MOCK development data on "
        f"{now}. Every number below is synthetic/demo and is not a finding. The assignment analysis is not complete.",
        "",
        "## 1. Memo to the CEO", "", not_ready, "",
        "## 2. Revenue bridge", "", not_ready, "",
        "Demo layout only (mock values, not findings):", "",
        "| Cause (MOCK) | Central pp | Low | High |", "|---|---|---|---|",
        *[f"| {b['cause']} | {b['central_pp']:+.2f} | {b['low_pp']:+.2f} | {b['high_pp']:+.2f} |" for b in bridge],
        f"| **Total (MOCK)** | **{k['revenue_change_pct']['value']:+.2f}** | | |", "",
        "## 3. Evidence for each initiative", "",
        *[f"- {i['name']}: recommendation **{i['recommendation']}** (no analysis yet)" for i in inits], "",
        "## 4. What the agent got wrong", "", not_ready, "",
        "## 5. Not done and not known", "",
        "- The synthetic dataset (`python3 -m datagen.generate`) has been generated but not analysed.",
        "- UNDERSTANDING.md is awaiting review; analysis starts only after that.", "",
    ]
    _write(REPORT, "\n".join(lines))
    return report_status(conn)
