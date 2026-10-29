"""Print the PERF line(s) and save the final screenshot from a saved REA perf-scenario result."""
import base64, json, re, sys
d = json.load(open(sys.argv[1]))
if 'records' in d and 'normalized_result' not in d:
    d = d['records'][-1]
steps = d['normalized_result']['steps']
last = steps[-1]['artifacts']
dom = json.dumps(last.get('dom', {}), ensure_ascii=False)
for m in re.findall(r'PERF[^"<]*?(?:DONE|ms)(?:[^"<]{0,200})', dom)[:2]:
    print(m.replace('\\n', ' | '))
shot = last.get('screenshot', {}).get('value', {})
if shot.get('data_base64') and len(sys.argv) > 2:
    open(sys.argv[2], 'wb').write(base64.b64decode(shot['data_base64']))
print('evidence', d['evidence_id'])
