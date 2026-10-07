import json,sys,datetime
for f in sys.argv[1:]:
  d=json.load(open(f)); print('==',f)
  for a in d.get('search_item_list',[]):
    s=a.get('statistics',{})
    print(datetime.datetime.fromtimestamp(a['create_time']).date(), s.get('digg_count'), s.get('play_count'), 'P' if '/photo/' in (a.get('url') or '') else 'V', (a.get('author') or {}).get('unique_id'), (a.get('desc') or '')[:90].replace('\n',' '))
