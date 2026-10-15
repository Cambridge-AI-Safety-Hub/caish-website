#!/usr/bin/env python3
"""Push the affiliation one-liners from data.js back to Airtable.

data.js is the deployed source of truth for the one-liners after the
2026-07-20 rewrite; Airtable still holds the older text. Run this once
with a token that has data.records:write on the HAP base, then rebuilds
via build.py will read the same text back.

Run:  python3 sync_affiliations.py            (uses keychain airtable-hap/pat)
      python3 sync_affiliations.py <token>    (explicit token)
"""
import json, os, subprocess, sys, urllib.request, urllib.error, urllib.parse

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'participants')
BASE, ONB = 'app8d6sDud8MgJ4XD', 'tblSlDG8s2J2YiV2D'


def token():
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    return subprocess.check_output(
        ['security', 'find-generic-password', '-s', 'airtable-hap', '-a', 'pat', '-w']
    ).decode().strip()


def main():
    pat = token()
    text = open(os.path.join(HERE, 'data.js')).read()
    prefix = 'window.PROFILES = '
    profiles = json.loads(text[len(prefix):text.index(';\n')])
    by_name = {p['name']: p['affiliation'] for p in profiles if p.get('affiliation')}

    # fetch record ids + names
    url = f'https://api.airtable.com/v0/{BASE}/{ONB}?' + urllib.parse.urlencode(
        [('pageSize', '100'), ('fields[]', 'full_name'), ('fields[]', 'affiliation')])
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {pat}'})
    recs = json.load(urllib.request.urlopen(req, timeout=30))['records']

    items = []
    for r in recs:
        name = (r['fields'].get('full_name') or '').strip()
        new = by_name.get(name)
        if new and new != (r['fields'].get('affiliation') or '').strip():
            items.append({'id': r['id'], 'fields': {'affiliation': new}})
    if not items:
        print('Airtable already matches data.js')
        return
    for i in range(0, len(items), 10):
        body = json.dumps({'records': items[i:i + 10]}).encode()
        req = urllib.request.Request(
            f'https://api.airtable.com/v0/{BASE}/{ONB}', data=body, method='PATCH',
            headers={'Authorization': f'Bearer {pat}', 'Content-Type': 'application/json'})
        json.load(urllib.request.urlopen(req, timeout=30))
    print(f'updated {len(items)} records')


if __name__ == '__main__':
    main()
