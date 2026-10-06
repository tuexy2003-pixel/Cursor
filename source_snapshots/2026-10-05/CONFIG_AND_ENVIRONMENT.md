# CONFIG & ENVIRONMENT
- Host: shared Linux box (the "box"), user `box`, TZ America/New_York. The agent works via Shell/Read plus a box desktop (1280×800) with a persistent browser.
- Roots: /workspace/creative-pipeline (all pipeline state), /home/box/agent-data/workflows (skills), /home/box/agent-data/agents/<id>/ (bot profile/settings), /workspace (misc scratch, older target-* folders, exports/).
- Runtimes: /usr/bin/python3 with Pillow 12.3.0 installed system-wide (numpy/opencv used by legacy scripts; versions pinned in engineering_source/_catchup_work/requirements.txt); node at /usr/bin/node (not used by the pipeline). No venv exists in creative-pipeline even though legacy scripts reference /workspace/creative-pipeline/venv. `zip` CLI is NOT installed (use python shutil). poppler-utils for PDFs.
- Dependency files: only _catchup_work/requirements.txt (legacy).
- Env var NAMES present: SCRAPECREATORS_API_KEY, APIFY_TOKEN, FISH_API_KEY. Scripts use ROOT, SMOKE_OUT, PYTHON.
- External services: chatgpt.com (signed-in browser session), Pinterest, DoorDash, Reddit, TikTok (saved browser logins), Target.com, Google search, ScrapeCreators API, Apify.
- Permissions: the agent can write anywhere under /workspace; skills are edited via the agent's UpdateSkill tool. Never delete originals.
- Formats: PNG finals; JPEG references. Final aspect 9:19.6 portrait (1206×2622 native iPhone; ChatGPT outputs about 851×1849 or 853×1844 are accepted). 1080×1920 / 9:16 is deprecated. Aspect changes happen through the image editor, not crop/stretch.
- Unknown: exact ChatGPT model/version used for edits (UNKNOWN). TikTok posting tooling (UNKNOWN; manual).
