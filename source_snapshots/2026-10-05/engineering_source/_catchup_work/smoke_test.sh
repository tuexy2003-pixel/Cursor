#!/usr/bin/env bash
# Portability smoke test: run from anywhere; uses the folder this script is in as ROOT.
set -u
export ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$ROOT/venv/bin/python"; [ -x "$PY" ] || PY=python3
OUT=${SMOKE_OUT:-/tmp/catchup_smoke}; mkdir -p "$OUT"
echo "ROOT=$ROOT  PY=$PY  OUT=$OUT"; fail=0
echo "== 0. leftover /workspace paths in code/specs"
if grep -rIl --include='*.py' --include='*.json' --include='*.sh' '/workspace' "$ROOT" | grep -v smoke_test.sh; then echo "FAIL: /workspace references above"; fail=1; else echo "OK: none"; fi
echo "== 1. chat builder on Isaiah's spec"
sed -e "s#\$ROOT/outputs/cand06_isaiah_chipotle/slide1_chat_916.png#$OUT/isaiah_chat_916.png#" \
    -e "s#\$ROOT/outputs/cand06_isaiah_chipotle/_w/slide1_chat_full.png#$OUT/isaiah_chat_full.png#" \
    "$ROOT/outputs/cand06_isaiah_chipotle/_w/chat_spec.json" > "$OUT/isaiah_spec.json"
"$PY" "$ROOT/outputs/_tools/build_imessage_ios26.py" "$OUT/isaiah_spec.json" > "$OUT/chat.log" 2>&1 || fail=1
grep -E "canvas|scale" "$OUT/chat.log"   # expect: (+0) scale->1920 0.732 ... free below header < ~100
echo "== 2. cand06 order build"
( cd "$OUT" && rm -rf cand06_w && cp -r "$ROOT/outputs/cand06_isaiah_chipotle/_w" cand06_w && cd cand06_w && ROOT="$ROOT" "$PY" build_cp.py ) 2>&1 | tail -n 3 || fail=1
echo "== 3. composite on plate B"
"$PY" "$ROOT/assets/phone_plates/composite_on_plate.py" user_B_bedsheet "$ROOT/outputs/cand06_isaiah_chipotle/order_screen_flat.png" "$OUT/isaiah_plateB.png" 2>&1 | tail -n 3 || fail=1
echo "== compare with shipped originals"
"$PY" - "$ROOT" "$OUT" <<'PYEOF' || fail=1
import sys, numpy as np
from PIL import Image
R,O=sys.argv[1],sys.argv[2]
pairs=[('chat', O+'/isaiah_chat_916.png', R+'/outputs/cand06_isaiah_chipotle/slide1_chat_916.png'),
       ('order', O+'/cand06_w/order_complete_cp.png', R+'/outputs/cand06_isaiah_chipotle/order_screen_flat.png'),
       ('plateB', O+'/isaiah_plateB.png', R+'/assets/phone_plates/tests/test_user_B_bedsheet.png')]
bad=0
for n,a,b in pairs:
    A=np.asarray(Image.open(a).convert('RGB')).astype(int); B=np.asarray(Image.open(b).convert('RGB')).astype(int)
    if A.shape!=B.shape: print(n,'SHAPE MISMATCH',A.shape,B.shape); bad=1; continue
    d=np.abs(A-B); print('%-6s size %s  identical=%s  mean|diff|=%.3f  max=%d  px>8: %.4f%%'%(n,A.shape[1::-1],(d.max()==0),d.mean(),d.max(),100*(d.max(2)>8).mean()))
sys.exit(bad)
PYEOF
[ $fail -eq 0 ] && echo "SMOKE TEST: PASS" || echo "SMOKE TEST: FAIL"
