# Decisions

One entry per update received and per change of direction. Newest last.
Editable in the app (Deliverables → Decisions); saved to this file.

## D1 — Assignment repository not available (2026-11-25)
- **Update:** The working folder was empty; no data, dashboards or scripts existed on the machine.
- **What changed:** UNDERSTANDING.md could not describe real files, so it was not written.
- **Now doing:** Built the app scaffold (SQLite pipeline, Python API, React UI, local analyst) on clearly labelled MOCK data.
- **Stopped doing:** Waiting for the repository.

## D2 — No real data: create a synthetic scenario (2026-11-25)
- **Update:** There are no assignment data files; we must create the problem and the solution ourselves.
- **What changed:** Every finding will describe a synthetic scenario, not a real company. The same agent designs the generator and analyses it, so the analysis is not blind.
- **Now doing:** `datagen/` generates a reproducible dataset (seed 20260930). Only `promo_annual_share` is calibrated, so the revenue dashboard shows -6.0%. All other values are documented assumptions (`data/ASSUMPTIONS.md`). Events are scaled to about 0.9M rows to respect the 4 GB / full-disk limits.
- **Stopped doing:** Treating the brief's +22% sign-ups and 41% -> 52% retention as targets. They emerge from the assumptions (synthetic dashboards show +19.7% and 46.5% -> 59.6%).

## D3 — Onboarding test countries changed (2026-11-25)
- **Update:** The first generation (CA + NL) produced only 470 experiment rows, too few for a usable randomized test.
- **Now doing:** Test countries are US + CA (1,725 rows). This is a design choice, recorded here because it changes statistical power.

## D4 — Push to GitHub (2026-11-25)
- **Update:** Push to `Akashgourav265/nexgile_test`.
- **What changed:** The remote already had an initial commit (LICENSE, README title).
- **Now doing:** Merged it (unrelated histories) and kept both. No force-push. The generated data stays git-ignored (reproducible with one command; adding 39 MB could not be undone without rewriting history).

## D5 — Time-boxed deliverables pass (2026-11-25)
- **Update:** Finish UNDERSTANDING.md (draft), Decisions and Report pages quickly; keep the app on mock data.
- **What changed:** "Generate report" must now write a real REPORT.md even before analysis.
- **Now doing:** Before analysis, generation writes a REPORT.md headed DEMO with no findings; all five sections say "not available".
- **Not done:** The instruction mentioned an "Upload tab we agreed on". No such tab exists and none was agreed, so none was built.

## D6 — Wording: "mock" replaced by "synthetic demo" (2026-11-25)
- **Update:** Remove the word "mock" from the user-facing app and the demo report, keeping clear Synthetic/Demo labels.
- **Now doing:** Labels read "Synthetic demo data" and "Demo ·". Internal identifiers (`--source mock`, `is_mock`) and earlier entries in this log are unchanged, as a record of what was said at the time. No values changed.

## D7 — UNDERSTANDING.md approved; analysis started (2026-11-25)
- **Update:** The user approved UNDERSTANDING.md and asked for the analysis, time-boxed to 2 minutes.
- **What changed:** UNDERSTANDING.md is locked as of commit `3a0e557`; it will not be edited again.
- **Now doing:** Plan step G.1 only. `python3 -m analysis.step1_revenue_definitions` independently reproduces the dashboard revenue change from the raw files (SYNTHETIC): -5.99% (shown as -6.0%). Removing 558 duplicate payment rows gives -6.01%; net of refunds, -6.30%. The duplicates do not change the headline.
- **Not done yet:** steps G.2-G.8 (bridge with ranges, payment failures, onboarding ITT, price DiD, referrals, tickets, app/report update). No initiative verdict has been formed.

## D8 — Request to update UNDERSTANDING.md after hand-in (2026-11-25)
- **Update:** The user asked to update UNDERSTANDING.md after approving it.
- **Decision:** The brief says it cannot be changed after hand-in, so post-hand-in updates go to UNDERSTANDING_ADDENDUM.md; the locked file is unchanged. Edit the original only if the user explicitly overrides this.
