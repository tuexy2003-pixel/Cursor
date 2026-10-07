# Preservation baseline

Frozen after the supplemental visual archives were attached and the verification edits were removed. Live provider execution remains `NOT_IMPLEMENTED`.

## Source snapshot

- Core snapshot: `source_snapshots/2026-10-05/`
- File count: 111
- Checksums: `source_snapshots/2026-10-05.SHA256SUMS`
- Checksum status: PASS. The directory stays read-only. The production-spec-qa file still contains `my birthday is literally tomorrow 😭`.
- Supplemental tree: `source_snapshots/supplements/2026-10-05/`
- Supplemental files: 19, checksums in `source_snapshots/supplements/2026-10-05.SHA256SUMS`
- Archive A content files: 13 under `examples/target_chore_stuff_v6/`
- Archive B content files: 5 under `examples/failures_v1_rejected/`
- `CURSOR_SPLIT_README.md` is stored with the supplements and is not an asset

## Database

- Migration revision: `b7c1a9e0d4f2` (revises `76f00d0e35cb`)
- Engine for this checkpoint: SQLite at `storage/creative_os.db` after `creative-os reset-db --seed`
- programs 1, accounts 3, campaigns 1, creatives 2
- story lock versions 1
- skill artifacts 15, skill versions 17
- policy rules 42
- assets 35, asset relations 20, example links 16
- regression tests 19, benchmarks 11, source artifacts 111
- experiments 0, model runs 0

The earlier operator correction to “tonight”, the verification experiment, and the stub model run are not in this database.

## Skills

- Imported skill files: 15
- Extra stored version: the live-heat query-hygiene playbook
- Current working versions: 14 remain `handoff-2026-10-05`. `production-spec-qa` current version is `working-2026-10-06` (`59f09c0b-1101-4580-9302-8cd652ca1b53`)
- Current-version statuses: 11 ACTIVE (including two frozen-active skills), 3 SUPPORTING, 1 LEGACY
- The imported production-spec-qa version is retained. Its text still contains the tomorrow example. The working version changes only that GOOD example to today. Approval actor: operator. Reason: human-authorized migration cleanup. Scope and rule kind stay GLOBAL HEURISTIC.

## Story locks

- Current approved Target version: version 1, imported from the 2026-10-05 lock, approved by Tyrel
- Floating hook: `my birthday is literally today 😭`
- Product: AirPods 5
- Total: $19.23
- No version 2 exists in the seeded database

## Assets

- Indexed rows from `ASSET_INDEX.json`: 25
- Child files with no separate index row: 10
- Total asset rows: 35
- Binary-present / hashes populated: 18 / 35
- Index files matched and hashed: 8
- Rights: USER_OWNED 1 (the operator’s Messages keyboard base), UNKNOWN 34
- No asset was marked CLEARED or REFERENCE_ONLY because the archives do not supply that evidence
- Stale rows: 10
- Indexed rows still without a file hash: 17
  - DoorDash base and step refs
  - Messages peek base, iOS 26 device chrome, retired Messages bases
  - Target reference bank directory, manifest, contact sheet, and read-first note
  - S2 ingredients directory (member files are hashed separately)
  - Target v1 directory plus v2 and v3 directories
  - current story-lock copy, benchmark spec, historical golden-example directory, viral corpus

`3_airpods4.jpg` is stale, product model AirPods 4, rights UNKNOWN, and is not an ingredient of the v6 S2 final.

`s2_user_airpods5.png` stays `stale=false` because the index says so. `STALE_ASSETS.md` still records that this base shows 4:31 and pickup Oct 23. That fact is an example link, not a rewritten stale flag.

## Regression tests

- Total: 19
- Deterministic: 7 (T04, T05, T06, T14, T16, T17, T18)
- Model review: 11
- Human review: 1 (T13)
- Stored evaluation mode is the status. Deterministic fixtures still return their checker result. Model-review cases return `MODEL_REVIEW_REQUIRED` and do not return PASS.

## Policy scope

Active rows after the scope correction:

| Scope | Kind | Active count |
| --- | --- | --- |
| GLOBAL | INVARIANT | 16 |
| GLOBAL | HEURISTIC | 13 |
| PROGRAM | INVARIANT | 1 |
| PROGRAM | PREFERENCE | 6 |
| ACCOUNT | PREFERENCE | 3 |
| CAMPAIGN |  | 0 |
| CREATIVE | LOCKED_VALUE | 1 |

Superseded, still stored: the global copy of money-path principle `principles-a-15`, and the program blob `principles-c-02` that named Maria, Sarah, and Brooke together.

Audit:

| Topic | Scope | Kind | Action |
| --- | --- | --- | --- |
| Explicit human correction, proof boundary, rights, stale-asset retention, no autonomous checkout | GLOBAL | INVARIANT | Kept. Section A item 14 still names DoorDash inside the global no-checkout rule. |
| Money-path `mydashperks.com` discount line | PROGRAM | INVARIANT | Moved off GLOBAL. The global row is superseded. |
| 15–20 life-world | PROGRAM | PREFERENCE | Already program-scoped |
| Target and DoorDash as the current ecosystems | PROGRAM | PREFERENCE | Already program-scoped |
| 9:19.6 output ratio | PROGRAM | PREFERENCE | Already program-scoped. The validator now applies it only to deliverable EXAMPLE assets. |
| Dark-mode iOS 26 | PROGRAM | PREFERENCE | Already program-scoped |
| Three-slide shape | GLOBAL | HEURISTIC | Source section B. Context may override. Not moved. |
| Floating TikTok hook | GLOBAL | HEURISTIC | Source section B. The today/tomorrow wording is an example, not a global hook law. |
| Maria / Sarah / Brooke lanes | ACCOUNT | PREFERENCE | Split out of the superseded program blob |
| AirPods 5, $19.23, today’s hook | CREATIVE | LOCKED_VALUE | Section D, bound to the Target creative |

Skill documents stay GLOBAL HEURISTIC. Lines inside them were not extracted into new global locked values.

## Validators

Implemented and run on the Target creative after the binary import:

| Check | Result |
| --- | --- |
| Provenance of hashed finals and matched files | PASS. These were WARNING when the bytes were absent. |
| Provenance of directory and still-absent index rows | WARNING. 8 warnings on this creative, including rows with no single file. |
| Rights export of the keyboard base | PASS (`USER_OWNED`) |
| Rights export of the order-details base and the AirPods 5 user screenshot | HUMAN_REVIEW_REQUIRED. UNKNOWN was not promoted. |
| Aspect of S1, S2, and S3 finals | PASS against the program 9:19.6 tolerance (851×1849 and 853×1844) |
| Aspect of product ingredients and bases | NOT_APPLICABLE |
| Aspect of rejected v1 slide 3 | FAIL. Measured 1080×1920. |
| Story-lock hook, AirPods 5 precedence, arithmetic | PASS. The stale AirPods 4 file passes lock precedence because it is marked stale and kept. |
| Lineage of S1 and S2 | PASS. Each recorded parent is a BASE. |
| Lineage of S3, v1 slide 1, and v1 slide 3 | HUMAN_REVIEW_REQUIRED. No parent was stated. |
| Recursive-edit fixture T18 | PASS as a checker. It still fails a derivative chain and withholds PASS when the chain is unknown. |

Creative validation totals on the Target creative: PASS 38, NOT_APPLICABLE 48, HUMAN_REVIEW_REQUIRED 8, WARNING 8, FAIL 1.

## Provenance

- Asset relations: 20
- Explicitly unresolved relationships: 6
  1. S3 final has no recorded base, ingredient, or reference parent.
  2. Whether the AirPods 5 user screenshot was cropped from the order-details plate is not stated.
  3. Rejected v1 slide 1 has no recorded base.
  4. Rejected v1 slide 3 has no recorded base.
  5. Brooke sequel and Dasher-got-nosy have no binary in these archives.
  6. DoorDash bases, the historical golden-example directory, and the viral corpus have no supplemental binaries.

Recorded relations include: keyboard base to S1 final, user AirPods 5 screenshot to S2 final, current product ingredients to S2, order-details plate to rejected v1 slide 2, and member links for ingredient files and v1 files.

Example links: 16. Current v6 slides are HOLDOUT for “SHE SAID IT WAS CHORE STUFF”, not WINNER. Rejected v1 slides are STALE. QA and provenance notes are REFERENCE. No weak-example asset was guessed.

## Known gaps

- 17 indexed assets still have no bytes in this environment
- Rights for 34 assets remain UNKNOWN
- S3 has no confident parent
- v2 and v3 directories are stale index rows without member files in these archives
- Parent/base chains that the notes do not name stay unresolved
- No live performance, comments, or provider execution
- Campaign scope has no rules
- The contact sheet in the core snapshot is a separate manifest image and was not treated as a new production base
