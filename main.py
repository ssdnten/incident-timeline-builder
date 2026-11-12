"""Merge CSV event exports into a UTC timeline with stable ordering, provenance and exact duplicate removal."""
import argparse
import csv
from datetime import datetime,timezone
import json
from pathlib import Path

REQUIRED={'timestamp','source','event_id','message'}

def build(rows):
    events={}
    duplicates=0
    for row in rows:
        if not REQUIRED <= row.keys() or any(not isinstance(row[k],str) or not row[k] for k in REQUIRED):
            raise ValueError('timestamp, source, event_id and message are required')
        time=datetime.fromisoformat(row['timestamp'].replace('Z','+00:00'))
        if time.tzinfo is None:
            raise ValueError('timestamps must include a UTC offset')
        normalized=time.astimezone(timezone.utc).isoformat().replace('+00:00','Z')
        key=(normalized,row['source'],row['event_id'],row['message'])
        origin=row.get('_origin','unknown')
        if key in events:
            duplicates+=1
            events[key]['origins'].append(origin)
        else:
            events[key]=dict(timestamp=normalized,source=row['source'],event_id=row['event_id'],message=row['message'],origins=[origin])
    # Sort actual instants; ISO strings with optional fractions are not safe sort keys.
    ordered=sorted(events.values(),key=lambda e:(datetime.fromisoformat(e['timestamp'].replace('Z','+00:00')),e['source'],e['event_id'],e['message']))
    return dict(events=ordered,duplicates_removed=duplicates)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs',type=Path,nargs='+')
    args=parser.parse_args()
    try:
        rows=[]
        for path in args.inputs:
            with path.open(encoding='utf-8',newline='') as handle:
                reader=csv.DictReader(handle)
                if not REQUIRED <= set(reader.fieldnames or []):
                    raise ValueError('missing required CSV columns')
                for number,row in enumerate(reader,2):
                    rows.append(dict(row,_origin=f'{path.name}:{number}'))
        print(json.dumps(build(rows),indent=2))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(2,f'error: {exc}\n')

if __name__=='__main__': main()
