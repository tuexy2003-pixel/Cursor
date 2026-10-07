#!/bin/bash
# usage: sc.sh "<query>" <date_posted> <sort_by> <cursor|""> <outfile>
q="$1"; d="$2"; s="$3"; c="$4"; out="$5"
KEY=$(python3 -c "import json; print(json.load(open('/home/box/agent-data/box-secrets.json'))['card']['SCRAPECREATORS_API_KEY'])")
args=(--get "https://api.scrapecreators.com/v1/tiktok/search/keyword" --data-urlencode "query=$q" --data-urlencode "date_posted=$d" --data-urlencode "sort_by=$s" --data-urlencode "trim=true")
[ -n "$c" ] && args+=(--data-urlencode "cursor=$c")
curl -sS -m 90 -H "x-api-key: $KEY" "${args[@]}" -o "$out"
n=$(cat raw/.reqcount); echo $((n+1)) > raw/.reqcount
python3 - "$out" <<'PY'
import json,sys
try:
  d=json.load(open(sys.argv[1]))
except Exception as e:
  print("PARSE ERR",e, open(sys.argv[1]).read()[:300]); sys.exit()
items=d.get('search_item_list') or d.get('items') or []
print(sys.argv[1], 'success',d.get('success'),'items',len(items),'cursor',d.get('cursor'),'charged',d.get('credits_charged'),'remaining',d.get('credits_remaining'), 'keys', list(d.keys())[:12])
PY
