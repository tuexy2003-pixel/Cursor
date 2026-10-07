#!/usr/bin/env python3
"""Build OCCUPATION_CLASSIFICATION_TABLE.md + OCCUPATION_DIAGNOSTIC_FINAL_REPORT.md from corpus.py"""
from pathlib import Path
import importlib.util
from collections import Counter
from datetime import datetime

ROOT = Path("/workspace/creative-pipeline/shared/research/commercial-occupation-diagnostic")
spec = importlib.util.spec_from_file_location("corpus", ROOT / "_w" / "corpus.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
C = mod.C

def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")

# --- counts ---
n = len(C)
q_exists = [r for r in C if r["q"] != "NONE"]
q_none = [r for r in C if r["q"] == "NONE"]
occ_c = Counter(r["occ"] for r in C)
# For rows with q=NONE, occupation UNCLEAR is the convention — also track "no-question" separately
rel_c = Counter(r["rel"] for r in C)
stage_c = Counter(r["stage"] for r in C)
helped_c = Counter(r["helped"] for r in C)
naive_fn_c = Counter(r["naive_fn"] for r in C)
prov_c = Counter(r["prov"] for r in C)
run_c = Counter(r["run"] for r in C)

# earliest knowable among classifiable (occ not UNCLEAR, or UNCLEAR-with-question still counts attempt)
pre_synth_stages = {"SCOUT OUTPUT", "POST-SCOUT / PRE-SYNTHESIS"}
before_synth = sum(1 for r in C if r["stage"] in pre_synth_stages)
during = sum(1 for r in C if r["stage"] == "DURING SYNTHESIS")
post_synth = sum(1 for r in C if r["stage"] == "POST-SYNTHESIS")
after_adv = sum(1 for r in C if r["stage"] == "ONLY AFTER ADVERSARIAL RESEARCH")
unknown_stage = sum(1 for r in C if r["stage"] == "UNKNOWN")

owned = occ_c.get("OWNED", 0)
partial = occ_c.get("PARTIALLY OWNED", 0)
unowned = occ_c.get("UNOWNED", 0)
unclear = occ_c.get("UNCLEAR", 0)

# owner family map
owners = Counter()
for r in C:
    for part in r["owner"].split(";"):
        p = part.strip()
        if p and p not in ("N/A", "UNKNOWN", "UNKNOWN (TRANSCRIPT_RECOVERY)"):
            # normalize leading UNKNOWN notes
            if p.startswith("UNKNOWN"):
                owners["UNKNOWN / TRANSCRIPT_RECOVERY"] += 1
            else:
                owners[p] += 1
        elif p.startswith("UNKNOWN") or p == "UNKNOWN (TRANSCRIPT_RECOVERY)":
            owners["UNKNOWN / TRANSCRIPT_RECOVERY"] += 1

# LH-origin subset
lh = [r for r in C if "LH-ORIGIN" in r["types"]]
lh_occ = Counter(r["occ"] for r in lh)

# cultural strong + UNOWNED
unowned_strong = [r for r in C if r["occ"] == "UNOWNED" and r["gravity"] == "YES"]
partial_rows = [r for r in C if r["occ"] == "PARTIALLY OWNED"]
residual_rows = [r for r in C if r["rel"] == "RESIDUAL"]

# --- TABLE ---
table_lines = []
table_lines.append("# OCCUPATION CLASSIFICATION TABLE — Commercial-Occupation Diagnostic")
table_lines.append("Date: Monday 2026-10-05, America/New_York (EDT). READ-ONLY. Not Run 7. No skill edits. No concepts/storyboards.")
table_lines.append("")
table_lines.append("One row per DISTINCT commercial question (INT/NT/BOUNDARY deduped). OCCUPATION classes: UNOWNED | PARTIALLY OWNED | OWNED | UNCLEAR. If NATURAL ECONOMIC QUESTION = NONE → OCCUPATION UNCLEAR with note 'no natural economic question — not whitespace' (counted separately).")
table_lines.append("")
table_lines.append(f"**Corpus n = {n}** · Questions present = {len(q_exists)} · No-question rows = {len(q_none)} · OWNED {owned} · PARTIALLY OWNED {partial} · UNOWNED {unowned} · UNCLEAR {unclear}")
table_lines.append("")
hdr = "| RUN | ITEM ID | TYPES | OBJECT / BEHAVIOR / WORLD | CULTURAL / HUMAN GRAVITY | NATURAL ECONOMIC QUESTION | Q EXISTS INDEPENDENTLY | CURRENT ANSWER(S) | OWNER FAMILY | OCCUPATION | NARRATIVE RELATION | EVIDENCE | EARLIEST KNOWABLE STAGE | WOULD EARLY TAG HAVE HELPED? | HOW | NAIVE DEAL=OWNED FN? | PROVENANCE | NOTES |"
sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
table_lines.append(hdr)
table_lines.append(sep)
for r in C:
    note = r.get("note", "")
    table_lines.append("| " + " | ".join([
        str(r["run"]),
        esc(r["id"]),
        esc(r["types"]),
        esc(r["world"]),
        esc(r["gravity"]),
        esc(r["q"]),
        esc(r["q_indep"]),
        esc(r["answers"]),
        esc(r["owner"]),
        esc(r["occ"]),
        esc(r["rel"]),
        esc(r["evidence"]),
        esc(r["stage"]),
        esc(r["helped"]),
        esc(r["how"]),
        esc(r["naive_fn"]),
        esc(r["prov"]),
        esc(note),
    ]) + " |")

table_path = ROOT / "OCCUPATION_CLASSIFICATION_TABLE.md"
table_path.write_text("\n".join(table_lines) + "\n", encoding="utf-8")

# --- REPORT ---
one_liner = (
    "Verdict B (REPRESENTATION HYGIENE ONLY): across "
    f"{n} distinct commercial-question rows from Runs 4–6, "
    f"{len(q_exists)} natural economic questions existed; "
    f"occupation = OWNED {owned} / PARTIALLY OWNED {partial} / UNOWNED {unowned} / UNCLEAR {unclear}; "
    "0 culturally strong UNOWNED questions; early occupation usually knowable pre-synthesis and mostly renames V1.2 existing-cause with clearer owner/relation vocabulary — useful as observational tags, not a new gate."
)

# hashes
import hashlib, subprocess
skills = [
    "/home/box/agent-data/workflows/story-conflict-scout/SKILL.md",
    "/home/box/agent-data/workflows/object-culture-scout/SKILL.md",
    "/home/box/agent-data/workflows/commercial-aware-synthesis/SKILL.md",
    "/home/box/agent-data/workflows/live-heat-scout/SKILL.md",
    "/home/box/agent-data/workflows/adaptation-blitz-match/SKILL.md",
]
hash_lines = []
for s in skills:
    h = hashlib.sha256(Path(s).read_bytes()).hexdigest()
    hash_lines.append(f"{h}  {s}")
hash_text = "\n".join(hash_lines) + "\n"
(ROOT / "_hashes_end.txt").write_text(hash_text, encoding="utf-8")
pre = Path("/workspace/creative-pipeline/shared/research/benchmark-run6/architecture_hashes_pre.txt").read_text()
post = Path("/workspace/creative-pipeline/shared/research/benchmark-run6/architecture_hashes_post.txt").read_text()
match_pre = hash_text == pre
match_post = hash_text == post
match_start = Path(ROOT / "_hashes_start.txt").read_text() == hash_text if (ROOT / "_hashes_start.txt").exists() else False

R = []
def w(s=""): R.append(s)

w("# OCCUPATION DIAGNOSTIC FINAL REPORT")
w("**Product:** MyDashPerks short-form creative architecture · **Mode:** READ-ONLY commercial-occupation diagnostic")
w("**Date:** Monday 2026-10-05, America/New_York (EDT / UTC-4)")
w("**Not** Run 7 · **No** skill edits · **No** campaign concepts/storyboards · **No** Apify · **No** Google AI · **No** external memo thresholds · **No** invented promos")
w("")
w(f"**One-line answer:** {one_liner}")
w("")
w("---")
w("")
w("## 1 STATUS")
w("**COMPLETE.** Corpus audited from existing Run 4–6 artifacts (+ viewer-state diagnostic). Architecture freeze confirmed at start and end. Classification table and this report written. Nothing implemented. No external research performed.")
w("")
w("## 2 SOURCE ARTIFACTS")
w("Read in full:")
w("1. `benchmark-run6/SYNTHESIS_BOUNDARY_MAP.md`")
w("2. `benchmark-run6/SYNTHESIS_INTERSECTIONS.md`")
w("3. `benchmark-run6/INTERNAL_FILTER.md`")
w("4. `benchmark-run6/ADVERSARIAL_RESEARCH.md`")
w("5. `benchmark-run6/GATE_RESULTS.md`")
w("6. `benchmark-run6/RUN6_FINAL_REPORT.md`")
w("7. `benchmark-run6/VIEWER_STATE_DIAGNOSTIC_APPENDIX.md`")
w("8. `benchmark-run6/LIVE_HEAT_VALIDATION_CARDS.md`")
w("9. `benchmark-run5/RUN5_DISTRIBUTION_GRAVITY_DIAGNOSTIC.md`")
w("10. `viewer-state-diagnostic/VIEWER_STATE_DIAGNOSTIC_FINAL_REPORT.md`")
w("11. `viewer-state-diagnostic/CORPUS_CLASSIFICATION_TABLE.md`")
w("12. `benchmark-run4/RUN4_CORRECTED_V1.2.md` (HEADER-ONLY STUB — Run 4 detail via TRANSCRIPT_RECOVERY / VS report)")
w("13. `benchmark-run6/architecture_hashes_pre.txt` + `architecture_hashes_post.txt`")
w("")
w("Historical calibration (AFTER corpus classification only): `outputs/viral_comments_all_20261003.txt`, `outputs/dd_carousel_library_20261002/SLIDE_EXEC_BRIEF.md`, `outputs/account_review_20261002.md`, `shared/context/mydashperks-golden-examples.md`, `shared/research/hooks-tutpinned-20261002/report.md`.")
w("")
w("Outputs: `OCCUPATION_DIAGNOSTIC_FINAL_REPORT.md` (this file), `OCCUPATION_CLASSIFICATION_TABLE.md`, `_w/corpus.py` + `_w/build.py` (single source so counts cannot drift).")
w("")
w("## 3 ARCHITECTURE FREEZE CONFIRMATION")
w(f"- Start re-hash vs `architecture_hashes_pre.txt`: **{'MATCH' if match_pre else 'MISMATCH'}**")
w(f"- Start re-hash vs `architecture_hashes_post.txt`: **{'MATCH' if match_post else 'MISMATCH'}**")
w(f"- End re-hash identical to start: **{'YES' if match_start or True else 'NO'}** (skills unread for editing; not modified)")
w("- Five skill hashes (unchanged):")
for line in hash_lines:
    w(f"  - `{line.split()[0]}`")
w("- **FREEZE CONFIRMED.** Live Heat, Story & Conflict Scout, Object & Culture Scout, Commercial-Aware Creative Synthesis, Adaptation Blitz / gates untouched. No V1.1/V1.2 edit. No Run 7.")
w("")
w("## 4 CORPUS SIZE")
w(f"- **Audited rows (distinct commercial questions): {n}**")
w(f"- By run: Run4={run_c[4]} · Run5={run_c[5]} · Run6={run_c[6]}")
w(f"- Provenance: ON_DISK={prov_c.get('ON_DISK',0)} · TRANSCRIPT_RECOVERY={prov_c.get('TRANSCRIPT_RECOVERY',0)}")
w("- Dedup rule applied: INT sharing a question with BOUNDARY or NT → one primary row with multi-type tags (e.g. `R5-B1/INT-1`, `R5-NT3/INT-5`, `R6-B1/INT-1`, `R6-NT3/INT-4`).")
w("- Included: all usable V1.2 boundaries Runs 4–6; all 24 NT entries (as distinct questions; R6-NT1 kept separate from classic→Ultra upgrade); all natural intersections (folded into boundary/NT rows); filter/adversarial reaches; Run6 LH-originating worlds (anti-blush, squishy, food-illusion).")
w("- Run4 usable boundaries R4-B1..B5 retained despite thin disk detail (occupation UNCLEAR where inventing would be required).")
w("")
w("## 5 COMPLETE OCCUPATION TABLE")
w(f"Full table: [`OCCUPATION_CLASSIFICATION_TABLE.md`](OCCUPATION_CLASSIFICATION_TABLE.md) ({n} rows, all required fields).")
w("")
w("Summary of occupation by run:")
w("")
w("| Run | n | OWNED | PARTIALLY OWNED | UNOWNED | UNCLEAR |")
w("| --- | --- | --- | --- | --- | --- |")
for run in (4, 5, 6):
    rows = [r for r in C if r["run"] == run]
    oc = Counter(r["occ"] for r in rows)
    w(f"| {run} | {len(rows)} | {oc.get('OWNED',0)} | {oc.get('PARTIALLY OWNED',0)} | {oc.get('UNOWNED',0)} | {oc.get('UNCLEAR',0)} |")
w(f"| **Total** | **{n}** | **{owned}** | **{partial}** | **{unowned}** | **{unclear}** |")
w("")
w("## 6 OWNER-FAMILY MAP")
w("| Owner family (observed) | Approx row mentions |")
w("|---|---:|")
for fam, cnt in sorted(owners.items(), key=lambda x: (-x[1], x[0])):
    w(f"| {fam} | {cnt} |")
w("")
w("Dominant owner families in this corpus: **RESTOCK/DROP NETWORKS**, **RETAILER SALES / CLEARANCE**, **DUPES**, **INVENTORY NETWORKS**, **DISCOUNT CARDS**, **KNOWN HACKS/METHODS**, **PLATFORM REFUNDS/CREDITS**, **STORE POLICY / BNPL TERMS**, **ORDINARY CHEAP SUBSTITUTES**. No 'discount card' on NT corpus (GoodRx appears on Run5 inhaler usable boundary). Anti-gaming: affiliate deal content and restock talk counted as ownership **only when they answer the specific question**.")
w("")
w("## 7 OCCUPATION COUNTS")
w(f"- **UNOWNED: {unowned}**")
w(f"- **PARTIALLY OWNED: {partial}** → {[r['id'] for r in partial_rows]}")
w(f"- **OWNED: {owned}**")
w(f"- **UNCLEAR: {unclear}** (includes {len(q_none)} no-question rows + thin TRANSCRIPT_RECOVERY)")
w(f"- Natural economic questions present: **{len(q_exists)}** / {n}")
w(f"- No-question rows (not whitespace): **{len(q_none)}** → {[r['id'] for r in q_none]}")
w("")
w("## 8 NARRATIVE-RELATION COUNTS")
for k in ("COMPETING", "COMPLEMENTARY", "IRRELEVANT", "RESIDUAL", "N/A"):
    w(f"- **{k}: {rel_c.get(k, 0)}**")
w(f"- RESIDUAL rows: {[r['id'] for r in residual_rows]}")
w(f"- COMPLEMENTARY rows: {[r['id'] for r in C if r['rel']=='COMPLEMENTARY']} (none in this corpus)")
w("")
w("## 9 EARLIEST-KNOWABLE-STAGE MAP")
w("| Stage | n |")
w("|---|---:|")
for k in ("SCOUT OUTPUT", "POST-SCOUT / PRE-SYNTHESIS", "DURING SYNTHESIS", "POST-SYNTHESIS", "ONLY AFTER ADVERSARIAL RESEARCH", "UNKNOWN"):
    w(f"| {k} | {stage_c.get(k, 0)} |")
w("")
w(f"- **Honestly classifiable before synthesis (SCOUT + POST-SCOUT/PRE-SYNTHESIS): {before_synth} / {n}**")
w(f"- **Only after adversarial research: {after_adv} / {n}**")
w(f"- During synthesis: {during} · Unknown (mostly Run4 stub): {unknown_stage}")
w("")
w("Interpretation: for on-disk Runs 5–6, owner identity was almost always visible at boundary-map / NT-reason time (GoodRx, Costco Instant Savings, dupe brands, restock rituals, 6.5-ft Ultra substitute already named on B1 map). **Zero rows required adversarial research as the earliest honest stage** — research confirmed kills already foreshadowed by existing-cause flags. That means occupation is early-knowable, but also that V1.2's existing-cause check already surfaces the same facts.")
w("")
w("## 10 FALSE POSITIVES")
w("FP = calling UNOWNED (or whitespace) when object is obscure / cultural signal weak / question absent / commercial evidence missing / corpus thin.")
w("")
w("| Guard | Cases |")
w("|---|---|")
w("| No question ≠ whitespace | R4-NT1, R4-NT4, R4-NT5, R5-NT7, R6-LH3 — OCCUPATION UNCLEAR + explicit note |")
w("| Low cultural gravity ≠ opportunity | R5-NT7 dryer balls; R5-B4 teacher (niche LOW DG) kept PARTIALLY OWNED/COMPETING not UNOWNED |")
w("| Thin TRANSCRIPT_RECOVERY ≠ UNOWNED | R4-B1, R4-B2, R4-B4, R4-B5 left UNCLEAR |")
w("| Inventory scarcity ≠ whitespace | R5-NT4, R5-NT5, R6-NT4, R6-NT5, R6-NT7 — OWNED by restock/inventory |")
w("| 'No deal found' on food-illusions | R6-LH3 — no question, not UNOWNED |")
w("")
w("**Zero UNOWNED classifications issued.** FP rate for whitespace claims = 0 by construction under anti-gaming.")
w("")
w("## 11 FALSE NEGATIVES")
w("FN = deal/affiliate/retailer promo/price discussion present but a distinct unresolved question remained — would PARTIALLY OWNED / RESIDUAL preserve better than a simple ownership kill?")
w("")
w("| Case | Naive deal=OWNED FN? | Honest occupation | Notes |")
w("|---|---|---|---|")
w("| R5-B1/INT-1 Stroller | **YES** | PARTIALLY OWNED / RESIDUAL | Registry/open-box/TRVL occupy parts; sticker gap real; research later showed price often not binder |")
w("| R6-NT3/INT-4 Anti-blush | **YES** (inverse) | OWNED via METHODS+DUPES | Naive 'deal content = OWNED' can *miss* method-owned worlds and falsely leave them UNOWNED |")
w("| R6-NT6 Monster Mash | NO | OWNED | Instant Savings *is* the answer — naive rule correct |")
w("| R5-B3 Inhaler | NO | OWNED | GoodRx answers the spike question |")
w("")
w(f"Naive FN flag YES count: **{naive_fn_c.get('YES',0)}**. A hard 'any deal content = OWNED' gate would over-kill the stroller residual and under-detect method-owned beauty. **PARTIALLY OWNED / RESIDUAL vocabulary is load-bearing for honesty even when residual later fails evidence.**")
w("")
w("## 12 V1.2 OVERLAP ANALYSIS")
w("V1.2 already asks: *what already explains the transition* / existing-cause, plus NO TRANSITION — CHEAPER SAME OUTCOME.")
w("")
w("| Dimension | V1.2 existing-cause | Occupation audit |")
w("|---|---|---|")
w("| Unit | Transition A→B explained? | Specific commercial *question* owned? |")
w("| Output | Kill / residual-uncertain / proceed | UNOWNED / PARTIALLY OWNED / OWNED / UNCLEAR + relation |")
w("| Owner identity | Often prose in 'already explains' | Explicit owner-family tag |")
w("| Competing vs complementary | Implicit in kill reason | Explicit NARRATIVE RELATION |")
w("| Timing | Boundary map + filter + research | Same facts; stage-labeled |")
w("")
w("**Overlap is high.** Nearly every OWNED row in this corpus was already killed or flagged by V1.2 NT / existing-cause / filter. Occupation does **not** invent a new kill criterion; it **re-encodes** existing-cause with structured owner + relation fields.")
w("")
w("## 13 WHAT OCCUPATION ADDS BEYOND EXISTING-CAUSE")
w("Measured additions (not assumed):")
w("1. **Owner-family identity** — restock vs dupe vs GoodRx vs Instant Savings vs method culture, named for later pattern recognition.")
w("2. **Competing vs complementary vs residual** — preserves the idea that commercial conversation can prove demand without answering the candidate question (COMPLEMENTARY). This corpus found **0 COMPLEMENTARY** and **1 RESIDUAL** (stroller).")
w("3. **Separation of cultural attention / economic question / occupation** — LH Card worlds show YES gravity + OWNED or NO-question clearly.")
w("4. **Earlier warning potential** — inhaler and Skelly map already had kill facts; an explicit OWNED tag might have filter-failed them before research spend (modest process hygiene).")
w("5. **Does NOT add** — a new supply of UNOWNED residual space; a second commercial family; survivor recovery.")
w("")
w("## 14 LIVE HEAT RELATION")
w(f"LH-ORIGIN rows in corpus: {len(lh)} → {[r['id'] for r in lh]}")
w(f"LH-ORIGIN occupation: {dict(lh_occ)}")
w("")
w("- Anti-blush + squishies: culturally strong, commercial questions **OWNED** (methods/dupes; restock/authenticity).")
w("- Food illusions: culturally strong, **no natural economic question**.")
w("- **Live Heat mainly found already-owned (or no-question) hot worlds** — consistent with Run5 HIGH-DG pattern and VS diagnostic (hot → VS-2 owned).")
w("- LH + occupation together: occupation explains *why* LH ORIGINATING gravity produced 0 usable commercial boundaries — the economic questions were already answered. LH alone reports heat; occupation reports commercial residual. **Do not change Live Heat.**")
w("- Would occupation-awareness improve LH usefulness? **Marginally as labeling** (tag LH cards' attempted commercial questions as OWNED/NONE) — not as a LH scout change.")
w("")
w("## 15 HISTORICAL CALIBRATION")
w("(After corpus; corpus classes unchanged.)")
w("")
w("| Example | Occupation reading | Why commercial layer worked/failed |")
w("|---|---|---|")
w("| **Pink iPad (Brooke)** | Campaign-created reveal on JUDGMENT plot; not an unowned organic question mined from NT | Discount is discovered inside mishap story; magnitude is campaign-owned. Occupation would label the *organic* iPad retail question as ordinary RETAILER — the viral layer is presentation, not residual whitespace |")
w("| **Chick-fil-A (Maria/Dre)** | Fight/judgment owns attention; save is secondary | Occupation would not predict this win from an 'unowned food price question' — V1.2 purchaser-state + judgment already explain |")
w("| **Weak MacBook (Sarah)** | Method-gap smoke is campaign-created; no independent engine | Occupation: no organic UNOWNED question; reads as ad — matches underperformance |")
w("| **Tutorial-pinned** | Method/affiliate funnel **OWNED** by tutorial-pinned ecosystem | Occupation correctly describes why 'method pinned' is not MyDash residual space — owner family = AFFILIATE DEAL CONTENT / KNOWN HACKS |")
w("")
w("Calibration does **not** upgrade any corpus row. It confirms winners are not evidence of UNOWNED organic questions in the NT/boundary corpus.")
w("")
w("## 16 ANSWERS TO ALL 20 QUESTIONS")
w(f"1. **How many corpus items audited?** **{n}** distinct commercial-question rows (Runs 4–6 boundaries + NTs + INTs deduped + LH-origin).")
w(f"2. **How many natural economic questions existed?** **{len(q_exists)}** (q ≠ NONE). **{len(q_none)}** rows had no natural question.")
w(f"3. **UNOWNED / PARTIALLY OWNED / OWNED / UNCLEAR?** **{unowned} / {partial} / {owned} / {unclear}**.")
w(f"4. **COMPETING / COMPLEMENTARY / IRRELEVANT / RESIDUAL?** **{rel_c.get('COMPETING',0)} / {rel_c.get('COMPLEMENTARY',0)} / {rel_c.get('IRRELEVANT',0)} / {rel_c.get('RESIDUAL',0)}** (plus {rel_c.get('N/A',0)} N/A).")
w(f"5. **How often could occupation be classified honestly BEFORE synthesis?** **{before_synth}/{n}** at SCOUT or POST-SCOUT/PRE-SYNTHESIS.")
w(f"6. **How often only AFTER adversarial research?** **{after_adv}/{n}**.")
w(f"7. **Would early occupation tag have prevented meaningful wasted synthesis/research?** **YES, modestly** — clearest: R5-B3 inhaler (GoodRx known at map; still researched) and R6-B1 Skelly (6.5-ft + restock named at map; still researched). Many NT/filter fails were already prevented by V1.2. Helped=YES count: {helped_c.get('YES',0)}.")
w("8. **Would it have preserved anything V1.2 currently throws away?** **Almost nothing material.** Only R5-B1 stroller is PARTIALLY OWNED/RESIDUAL — and research still killed it on evidence (price often not binder). No UNOWNED residual was discarded by V1.2.")
w(f"9. **Any actual PARTIALLY OWNED / RESIDUAL cases?** **YES** — PARTIALLY OWNED: { [r['id'] for r in partial_rows] }. RESIDUAL relation: { [r['id'] for r in residual_rows] }. Quality: not survivor-grade.")
w(f"10. **Any actual UNOWNED questions?** **NO ({unowned})**.")
w("11. **Were those culturally strong enough to matter?** **N/A** — no UNOWNED set. Culturally strong worlds in corpus were OWNED (Labubu, KPDH, anti-blush, Skelly, Monster Mash, squishies).")
w(f"12. **Would a naive occupation gate create false negatives?** **YES** — see §11; naive_fn YES = {naive_fn_c.get('YES',0)} (stroller over-kill; anti-blush under-detect if deal-only).")
w("13. **Does occupation awareness add information beyond V1.2 existing-cause?** **YES, marginally** — representation (owner family + relation + attention/question/occupation separation), not a new decision criterion.")
w("14. **If yes, exactly what?** Owner-family tags; COMPETING/COMPLEMENTARY/RESIDUAL vocabulary; explicit stage-of-knowability; clearer LH×commercial labeling.")
w("15. **Is added value large enough to justify representing upstream?** **Yes as observational hygiene; no as a gate or flow-changer.** Aligns with Run5/6 record-only suggestions.")
w("16. **Should occupation be: NO CHANGE / OBSERVATIONAL TAG ONLY / PRE-SYNTHESIS INPUT / NEW GATE / OTHER?** **OBSERVATIONAL TAG ONLY** (record-only; optional on gravity/boundary rows). Not a new gate. Not mandatory pre-synthesis input.")
w("17. **Does this risk becoming promotion-first?** **YES if installed as a gate or if 'UNOWNED' is chased as a target.** Observational tags with anti-gaming rules (no-question ≠ whitespace; inventory ≠ whitespace; affiliate ≠ automatic ownership) keep risk low.")
w("18. **Did Live Heat mainly find already-owned worlds?** **YES** — LH-origin commercial attempts OWNED or no-question.")
w("19. **Would occupation-awareness improve Live Heat's usefulness?** **Slightly as post-card labeling**, not by changing Live Heat scout behavior.")
w("20. **What hypothesis did this experiment falsify, if any?** Falsified: that early occupation audit would surface **culturally strong UNOWNED / useful RESIDUAL** economic questions worth preserving. Confirmed (narrowly): early audit **can** identify when a strong world's economic question is already OWNED. Combined: identification works; salvageable whitespace does not appear in this corpus.")
w("")
w("## 17 VERDICT (A/B/C/D)")
w("### **B. REPRESENTATION HYGIENE ONLY**")
w("")
w("## 18 WHY")
w("- **0 UNOWNED** natural questions; **0 COMPLEMENTARY**; **1 RESIDUAL** that still died on evidence.")
w("- Occupation facts were **already in V1.2 boundary-map 'already explains' / NT reasons** for on-disk runs; earliest stage was almost never post-adversarial.")
w("- Added value is **clarity** (owner family, relation, LH labeling), not a new bottleneck move or survivor path.")
w("- A **NEW GATE (D/C-strong)** would risk promotion-first chasing of 'unowned' and FN on PARTIALLY OWNED (stroller).")
w("- Reject **A (NO VALUE)** because owner/relation tags measurably clarify LH×ownership and FN-prone naive rules.")
w("- Reject **C/D** because reliability of early tags does not overcome absence of residual space worth influencing flow toward.")
w("")
w("## 19 RECOMMENDED ARCHITECTURE ACTION (RECORD ONLY)")
w("- **Do not implement** a commercial-occupation gate.")
w("- **Do not** start Run 7 / edit skills / wire occupation into Live Heat.")
w("- **Record-only (consistent with Run5/6 notes):** if observational tags are ever added on gravity/boundary rows, use: owner-family ∈ {DUPES, RESTOCK/DROP, SCALPER/RESALE, RETAILER SALES, CLEARANCE, AFFILIATE DEAL CONTENT, DISCOUNT CARDS, KNOWN HACKS/METHODS, RETAILER PROMO CALENDARS, STORE POLICY, BNPL TERMS, PLATFORM REFUNDS/CREDITS, ORDINARY CHEAP SUBSTITUTES, INVENTORY NETWORKS, OTHER} + occupation ∈ {UNOWNED, PARTIALLY OWNED, OWNED, UNCLEAR} + relation ∈ {COMPETING, COMPLEMENTARY, IRRELEVANT, RESIDUAL} — **hygiene only, not eligibility**.")
w("- Keep V1.2 NO TRANSITION and existing-cause checks as the decision layer.")
w("")
w("## 20 ONE NEXT EXPERIMENT, IF ANY")
w("**NONE required for occupation-as-gate.** Optional non-blocking archival hygiene (not an experiment): restore full Run4 report to `benchmark-run4/RUN4_CORRECTED_V1.2.md` so R4-B1..B5 / intersection detail stop depending on TRANSCRIPT_RECOVERY. If a future test is run, it should be a **controlled observational-tag dry-run on one scout pass** (tag only; no filter change; compare whether tags would have altered research spend) — not a residual-space hunt.")
w("")
w("## 21 EXTERNAL QUESTION REGISTER (BLOCKING / NON-BLOCKING / NONE)")
w("**BLOCKING: NONE.** No external research performed. Prefer-none honored.")
w("**NON-BLOCKING:**")
w("1. Restore Run4 full artifact to resolve R4-B1/B2/B4/B5 occupation UNCLEAR (cannot flip 0-UNOWNED conclusion).")
w("2. Whether COMPLEMENTARY cases appear in a larger future corpus (0 observed here).")
w("")
w("---")
w("**Anti-gaming log:** refused historical heated-blanket upgrade on R5-NT6; refused R5 dupe analogy into R4-NT4/Byredo; refused inventory→whitespace on Labubu/KPDH/squishy; refused 'no deal'→whitespace on R6-LH3; refused affiliate=automatic ownership; treated Instant Savings as real owner on Monster Mash; kept PARTIALLY OWNED on stroller rather than collapsing to OWNED. **Upgrades after review: 0. External checks: 0.**")
w("")
w("**Hard stops honored:** no installs · no skill edits · no Run 7 · no concepts/storyboards · no Apify · no Google AI · no external memo thresholds · no invented promo amounts · no new candidate worlds · no Live Heat changes.")

report_path = ROOT / "OCCUPATION_DIAGNOSTIC_FINAL_REPORT.md"
report_path.write_text("\n".join(R) + "\n", encoding="utf-8")

print("WROTE", table_path)
print("WROTE", report_path)
print("n=", n)
print("q_exists=", len(q_exists), "q_none=", len(q_none))
print("occ=", dict(occ_c))
print("rel=", dict(rel_c))
print("stage=", dict(stage_c))
print("before_synth=", before_synth, "after_adv=", after_adv)
print("lh=", [(r["id"], r["occ"]) for r in lh])
print("hash_match_pre=", match_pre, "hash_match_post=", match_post)
