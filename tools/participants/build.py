#!/usr/bin/env python3
"""Build the HAP participant directory from Airtable onboarding data.

Pulls ONLY public-safe fields, filters to website_consent == "Yes", downloads
headshots locally (Airtable attachment URLs expire), and writes data.js.

Sensitive fields (passport, DOB, emergency contact, dietary, accessibility,
private notes, email) are never requested from Airtable, so they cannot leak.

Run from the repo root with an Airtable token that can read the HAP base:
    AIRTABLE_TOKEN=... python3 tools/participants/build.py
It rewrites participants/data.js and participants/images/.
"""
import json, subprocess, urllib.request, urllib.parse, os, sys, mimetypes

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'participants')
IMG_DIR = os.path.join(HERE, 'images')
BASE, ONB = 'app8d6sDud8MgJ4XD', 'tblSlDG8s2J2YiV2D'

# The ONLY fields we ever pull. Everything else stays in Airtable.
PUBLIC_FIELDS = ['full_name', 'pronouns', 'affiliation', 'bio', 'link', 'website_consent', 'photo_consent', 'headshot']


def keychain(service, account):
    if os.environ.get('AIRTABLE_TOKEN'):
        return os.environ['AIRTABLE_TOKEN']
    return subprocess.check_output(
        ['security', 'find-generic-password', '-s', service, '-a', account, '-w']
    ).decode().strip()


def airtable(pat):
    recs, offset = [], None
    params = [('pageSize', '100')] + [('fields[]', f) for f in PUBLIC_FIELDS]
    while True:
        q = params + ([('offset', offset)] if offset else [])
        url = f'https://api.airtable.com/v0/{BASE}/{ONB}?' + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {pat}'})
        d = json.load(urllib.request.urlopen(req, timeout=30))
        recs += d['records']
        offset = d.get('offset')
        if not offset:
            return recs


def clean_link(url):
    if not url:
        return ''
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def download_headshot(att, recid):
    """Download the first image attachment, convert to web-safe JPEG, return
    local filename or ''. Phones upload HEIC, which browsers cannot render, so
    everything is normalised to JPEG via sips regardless of source format."""
    try:
        url = att.get('url')
        if not url:
            return ''
        raw = os.path.join(IMG_DIR, f'{recid}.orig')
        with urllib.request.urlopen(url, timeout=30) as r, open(raw, 'wb') as fh:
            fh.write(r.read())
        # convert to JPEG and downscale in one pass (handles HEIC, PNG, etc.)
        fname = f'{recid}.jpg'
        path = os.path.join(IMG_DIR, fname)
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-Z', '512', raw, '--out', path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            os.remove(raw)
        except OSError:
            pass
        if not os.path.exists(path):
            print(f'  ! headshot conversion failed for {recid}')
            return ''
        return f'images/{fname}'
    except Exception as e:
        print(f'  ! headshot download failed for {recid}: {e}')
        return ''


def existing_profiles():
    """Return the current generated profiles so manual public copy can survive rebuilds."""
    path = os.path.join(HERE, 'data.js')
    try:
        text = open(path).read()
        prefix = 'window.PROFILES = '
        start = text.index(prefix) + len(prefix)
        end = text.index(';\n', start)
        return {p.get('name'): p for p in json.loads(text[start:end])}
    except Exception:
        return {}


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    try:
        recs = airtable(keychain('airtable-hap', 'pat'))
    except Exception as e:
        sys.exit(f'Airtable fetch failed: {e}')

    existing = existing_profiles()
    profiles, skipped = [], []
    for r in recs:
        f = r['fields']
        name = (f.get('full_name') or '').strip()
        if (f.get('website_consent') or '').strip().lower() != 'yes':
            skipped.append(name or r['id'])
            continue
        photo = ''
        if (f.get('photo_consent') or '').strip().lower() == 'yes' and f.get('headshot'):
            photo = download_headshot(f['headshot'][0], r['id'])
        prior = existing.get(name, {})
        affiliation = (f.get('affiliation') or '').strip() or prior.get('affiliation', '')
        profiles.append({
            'name': name,
            'pronouns': (f.get('pronouns') or '').strip(),
            'affiliation': affiliation,
            'bio': (f.get('bio') or '').strip(),
            'link': clean_link(f.get('link')),
            'photo': photo,
        })

    profiles.sort(key=lambda p: p['name'].lower())
    out = os.path.join(HERE, 'data.js')
    with open(out, 'w') as fh:
        fh.write('window.PROFILES = ' + json.dumps(profiles, ensure_ascii=False, indent=1) + ';\n')
    print(f'wrote {out}')
    print(f'  {len(profiles)} profiles ({sum(1 for p in profiles if p["photo"])} with photo)')
    print(f'  excluded (no website consent): {skipped or "none"}')


if __name__ == '__main__':
    main()
