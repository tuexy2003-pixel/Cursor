import json,glob,datetime,re,csv
CUT=datetime.datetime(2026,8,11,tzinfo=datetime.timezone.utc)  # 45 days before 2026-09-25
raw={}; total=0
for f in sorted(glob.glob('raw/kw_*.json')):
    d=json.load(open(f))
    for a in d.get('search_item_list',[]):
        total+=1
        aid=a['aweme_id']
        if aid in raw:
            raw[aid]['_queries'].add(f.split('/')[-1]); continue
        a['_queries']={f.split('/')[-1]}
        raw[aid]=a
print('raw items',total,'unique',len(raw))
recent={k:v for k,v in raw.items() if datetime.datetime.fromtimestamp(v['create_time'],datetime.timezone.utc)>=CUT}
print('recent<=45d',len(recent))
DEAL=r"target|walmart|coach|kohl|buildabear|build a bear|bestbuy|olivegarden|redlobster|mcdonald|ubereat|doordash|costco|aldi|samsclub|heb\b|hebfind|meijer|discount|deal|coupon|giftcard|gift card|studentdiscount|starbucks|cheesecake|ihop|windsor|sephora|spirithalloween|fuggler|barnesandnoble|primark|bandm|dollartree|fivebelow|nordstrom|aritzia|hollister|ross|owala|amazonfinds|justeat|fetch|sweatcoin|tiktokcoupon|playstation|voucher|promocode|clearance|offer|\$\d|boobasket|carseat|cloudcouch|groceryshopping|groceryhaul|budgetfriendly|woolworths|iphone18|evenflo|lego|snoopy|calicocritters|free ?food|restock|method"
OFF=r"roblox|headless|korblox|manifest|capcut|trollface|sigma|makeup|brow|curls|hairst|ponytail|tattoo|stickandpoke|minecraft|sourdough|squishy|pinmaker|открытк|hypic|pizza steel|dough and sauce|ingrédients|mixedwrestling|couplegoals|pinning a video|pin posts|fix your pinned|erasermethode|freeform|bio deserves|animation course"
rows=[]
for k,a in recent.items():
    desc=(a.get('desc') or '')
    low=desc.lower()
    s=a['statistics']
    on = bool(re.search(DEAL,low)) and not re.search(OFF,low)
    rows.append(dict(id=k,url=a.get('url'),author=(a.get('author') or {}).get('unique_id'),date=a['create_time_utc'][:10],
        likes=s.get('digg_count'),plays=s.get('play_count'),comments=s.get('comment_count'),shares=s.get('share_count'),saves=s.get('collect_count'),
        format='carousel' if '/photo/' in (a.get('url') or '') else 'video',caption=desc.replace('\n',' '),on=on,queries=';'.join(sorted(a['_queries']))))
rows.sort(key=lambda r:-r['likes'])
json.dump(rows,open('pool_recent_all.json','w'),indent=1)
on=[r for r in rows if r['on']]
print('on-topic auto',len(on))
for i,r in enumerate(rows[:120]):
    print(i, 'ON ' if r['on'] else 'off', r['date'], r['likes'], r['author'], r['caption'][:80])
