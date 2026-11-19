"""Offline Sitemap XML check with optional exported crawl evidence."""
import argparse
import csv
import gzip
import json
import re
import xml.etree.ElementTree as ET
import zlib
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 50 * 1024 * 1024
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def parse_url(value):
    p = urlsplit(value)
    _ = p.port
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password or any(c.isspace() for c in value):
        raise ValueError('Not an absolute HTTP(S) URL')
    return p


def valid_date(value):
    try:
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            date.fromisoformat(value)
        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
            zone = re.search(r'([+-])(\d{2}):(\d{2})$', value)
            if zone:
                hours, minutes = int(zone[2]), int(zone[3])
                if hours > 14 or minutes > 59 or (hours == 14 and minutes != 0):
                    return False
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            return False
        return True
    except ValueError:
        return False


def audit(data, host, crawl=None):
    if len(data) > MAX_BYTES:
        raise ValueError('Uncompressed XML exceeds 50 MiB')
    # Refuse DTD/entity declarations even in UTF-16 input before XML parsing.
    if re.search(br'<!\s*(?:DOCTYPE|ENTITY)', data.replace(b'\x00', b''), re.I):
        raise ValueError('DTD/entities are not supported')
    root = ET.fromstring(data)
    kind = root.tag.rsplit('}', 1)[-1]
    if kind not in ('urlset', 'sitemapindex'):
        raise ValueError('Expected urlset or sitemapindex')
    issues = []
    if root.tag != NS + kind:
        issues.append({'type': 'namespace_mismatch'})
    prefix = NS if root.tag.startswith(NS) else ''
    element = 'url' if kind == 'urlset' else 'sitemap'
    entries = []
    records = defaultdict(list)
    if crawl is not None:
        for row in crawl:
            records[row['url']].append(row)
    for i, node in enumerate(root.findall(prefix + element), 1):
        locs = node.findall(prefix + 'loc')
        loc = (locs[0].text or '').strip() if locs else ''
        if len(locs) != 1:
            issues.append({'type': 'loc_count', 'entry': i, 'count': len(locs)})
        record = {'entry': i, 'url': loc, 'network_status': 'unverified'}
        entries.append(record)
        try:
            p = parse_url(loc)
            if p.hostname.lower() != host.lower():
                issues.append({'type': 'outside_host', 'entry': i, 'url': loc})
        except ValueError:
            issues.append({'type': 'invalid_url', 'entry': i, 'url': loc})
        lm = node.find(prefix + 'lastmod')
        if lm is not None and not valid_date((lm.text or '').strip()):
            issues.append({'type': 'invalid_lastmod', 'entry': i, 'value': lm.text})
        if kind == 'urlset' and loc in records:
            samples = records[loc]
            record['crawl_evidence'] = samples
            if len(samples) != 1:
                issues.append({'type': 'multiple_crawl_records', 'url': loc})
                continue
            r = samples[0]
            status = (r.get('status') or '').strip()
            if not re.fullmatch(r'[1-5]\d{2}', status):
                issues.append({'type': 'invalid_crawl_status', 'url': loc, 'value': status})
            else:
                record['network_status'] = 'provided_export:' + status
                if status != '200':
                    issues.append({'type': 'non_200', 'url': loc, 'status': status})
            for field in ('final_url', 'canonical'):
                if r.get(field) and r[field] != loc:
                    issues.append({'type': field + '_differs', 'url': loc, 'value': r[field]})
    for url, count in Counter(e['url'] for e in entries if e['url']).items():
        if count > 1:
            issues.append({'type': 'duplicate_url', 'url': url, 'count': count})
    if len(entries) > 50000:
        issues.append({'type': 'too_many_entries', 'count': len(entries)})
    if not entries:
        issues.append({'type': 'no_entries'})
    return {'kind': kind, 'entries': entries, 'issues': issues,
            'unverified': ['indexing', 'actual lastmod truth', 'live HTTP responses'] + (['child sitemaps'] if kind == 'sitemapindex' else []),
            'scope': 'local XML and optional supplied crawl export'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--host', required=True, help='Exact hostname, e.g. www.example.com')
    p.add_argument('--crawl', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        opener = gzip.open if a.input.suffix == '.gz' else open
        with opener(a.input, 'rb') as f:
            data = f.read(MAX_BYTES + 1)
        crawl = None
        if a.crawl:
            with a.crawl.open(encoding='utf-8-sig', newline='') as f:
                r = csv.DictReader(f)
                if not {'url', 'status', 'final_url', 'canonical'}.issubset(r.fieldnames or []):
                    raise ValueError('crawl CSV requires url,status,final_url,canonical')
                crawl = list(r)
        host_url = parse_url('https://' + a.host)
        if host_url.port is not None or host_url.path or host_url.query or host_url.fragment or host_url.hostname != a.host.lower():
            raise ValueError('--host must be a hostname, not a URL')
        result = audit(data, a.host, crawl)
        with a.output.open('x', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(json.dumps({'kind': result['kind'], 'entries': len(result['entries']), 'issues': len(result['issues'])}))
    except (OSError, EOFError, zlib.error, ValueError, ET.ParseError, csv.Error) as e:
        p.exit(2, str(e) + '\n')


if __name__ == '__main__':
    main()
