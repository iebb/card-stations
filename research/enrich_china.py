#!/usr/bin/env python3
"""Conservative Chinese station enrichment from cached, city-scoped OSM queries.

No card codes or native primary names are generated. Existing nonempty fields are
preserved except unreferenced approximate coordinates when a unique exact station
identity is established. Source snapshots are public OSM data and are not vendored.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

COLUMNS = ['code','station_code','name','name_en','name_ja','name_hanja','name_zh_hans','name_zh_hant','line_code','line','latitude','longitude','osm_ref']
LANGUAGES = {'name_en':('name:en',),'name_ja':('name:ja',),'name_zh_hans':('name:zh-Hans','name:zh'),'name_zh_hant':('name:zh-Hant',)}


def normalized(value):
    return ''.join(unicodedata.normalize('NFKC',value or '').split()).translate(str.maketrans('','','()（）'))


def chinese_component(tags):
    """Read a Chinese + explicitly tagged Uyghur bilingual label without fuzzy matching."""
    clean=lambda value:''.join(c for c in value if unicodedata.category(c)!='Cf').strip()
    name=clean(tags.get('name',''));uyghur=clean(tags.get('name:ug',''))
    if not uyghur or not name.endswith(uyghur):return ''
    prefix=name[:-len(uyghur)]
    if not prefix or not prefix[-1].isspace():return ''
    chinese=prefix.strip()
    return chinese if re.fullmatch(r'[\u3400-\u9fff]+',chinese) else ''


def native_names(tags):
    result=set()
    for key in ('name','name:zh','name:zh-Hans'):
        value=tags.get(key,'')
        result.update(normalized(part) for part in value.split(';') if normalized(part))
    component=chinese_component(tags)
    if component:result.add(normalized(component))
    return result


def point(element):
    center=element.get('center',{})
    lat=element.get('lat',center.get('lat'))
    lon=element.get('lon',center.get('lon'))
    return (float(lon),float(lat)) if lat is not None and lon is not None else None


def metres(a,b):
    return math.hypot((a[0]-b[0])*math.cos(math.radians((a[1]+b[1])/2)),a[1]-b[1])*111195.08


def station_rank(e,kind=''):
    tags=e.get('tags',{})
    if tags.get('railway')=='subway_entrance' or 'entrance' in tags:
        return 0
    bus=tags.get('highway')=='bus_stop' or tags.get('amenity')=='bus_station' or (tags.get('bus')=='yes' and tags.get('public_transport') in ('station','platform'))
    rail=tags.get('railway') in ('station','halt','tram_stop') or tags.get('station') in ('subway','light_rail') or (tags.get('public_transport') in ('station','stop_area') and not bus)
    if kind in ('BRT','公交','自行车'):
        if not bus:return 0
        if kind=='BRT' and tags.get('brt')!='yes' and not re.search(r'brt|快速公交',' '.join(tags.get(k,'') for k in ('network','operator','ref','route_ref')),re.I):return 0
    elif not rail:return 0
    if tags.get('railway')=='station' or tags.get('station')=='subway':return 10 if e['type']=='node' else 8
    if tags.get('public_transport')=='station':return 9 if e['type']=='node' else 7
    if tags.get('railway')=='tram_stop':return 8
    if bus:return 6 if e['type']=='node' else 4
    return 3


def osm_key(e):return f"{e['type']}/{e['id']}"


def line_label(tags):
    ref=tags.get('ref','').strip()
    if re.fullmatch('[0-9]+',ref):return ref+'号线'
    if re.fullmatch('[Ss][0-9]+',ref):return ref.upper()+'号线'
    for key in ('name:zh','name'):
        match=re.search(r'([0-9一二三四五六七八九十]+号线)',tags.get(key,''))
        if match:return match.group(1)
    if ref and len(ref)<=24 and not any(c in ref for c in ';|/') :return ref
    return ''


def build_route_memberships(elements):
    areas=defaultdict(set)
    known_stops=set()
    for e in elements:
        tags=e.get('tags',{})
        if tags.get('railway') in ('station','halt','tram_stop','stop') or tags.get('station') in ('subway','light_rail') or tags.get('public_transport') in ('station','platform','stop_position'):
            known_stops.add(osm_key(e))
    for e in elements:
        if e['type']=='relation' and e.get('tags',{}).get('public_transport')=='stop_area':
            members={f"{m['type']}/{m['ref']}" for m in e.get('members',[]) if m['type'] in ('node','way')}
            members.add(osm_key(e))
            for m in e.get('members',[]):
                if m.get('role') in ('station','stop','platform','stop_position') or any(word in m.get('role','') for word in ('stop','platform')):
                    known_stops.add(f"{m['type']}/{m['ref']}")
            for key in members:areas[key].update(members)
    membership=defaultdict(set)
    refs=defaultdict(set)
    for e in elements:
        tags=e.get('tags',{})
        if e['type']!='relation' or tags.get('type')!='route' or tags.get('route') not in ('subway','light_rail','monorail','tram'):
            continue
        label=line_label(tags)
        if not label:continue
        for m in e.get('members',[]):
            # Require explicit roles or independently identified station/stop/platform objects.
            if m['type'] not in ('node','way'):continue
            key=f"{m['type']}/{m['ref']}"
            role=m.get('role','')
            if role and not any(word in role for word in ('stop','platform')) and role!='station':continue
            if not role and key not in known_stops:continue
            for joined in {key}|areas.get(key,set()):
                membership[joined].add(label);refs[(joined,label)].add(e['id'])
    return membership,refs


def read_csv(path):
    with path.open(encoding='utf-8',newline='') as f:
        r=csv.DictReader(f);return r.fieldnames,list(r)


def write_csv(path,rows,original):
    columns=[c for c in COLUMNS if c in original or any(r.get(c) for r in rows)]
    # Do not retain a column merely because its old importer supplied it empty.
    columns=[c for c in columns if c in ('code','name') or any(r.get(c) for r in rows)]
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,lineterminator='\n',extrasaction='ignore');w.writeheader()
        for row in sorted(rows,key=lambda r:r['code']):w.writerow({c:row.get(c,'') for c in columns})


def enrich_city(path,cache,source_types,reviewed_coordinates,reference_cities,equivalences):
    original,rows=read_csv(path)
    snapshot=cache/(path.stem+'.json')
    audit={'city_code':path.stem,'records':len(rows),'snapshot':None,'changes':Counter(),'unresolved':[],'rejected_matches':[],'line_evidence':[],'bilingual_name_evidence':[]}
    if not snapshot.exists():
        audit['unresolved']=[{'code':r['code'],'name':r['name'],'reason':'city snapshot unavailable'} for r in rows]
        return audit,[]
    raw=snapshot.read_bytes();payload=json.loads(raw);elements=payload['elements']
    supplement=cache/(path.stem+'-supplement.json')
    supplement_info=None
    if supplement.exists():
        extra=supplement.read_bytes();supplement_payload=json.loads(extra)
        joined={osm_key(e):e for e in elements}
        joined.update({osm_key(e):e for e in supplement_payload['elements']})
        elements=list(joined.values())
        supplement_info={'sha256':hashlib.sha256(extra).hexdigest(),'osm_base':supplement_payload.get('osm3s',{}).get('timestamp_osm_base'),'elements':len(supplement_payload['elements'])}
    audit['snapshot']={'sha256':hashlib.sha256(raw).hexdigest(),'osm_base':payload.get('osm3s',{}).get('timestamp_osm_base'),'elements':len(payload['elements'])}
    audit['supplement']=supplement_info
    by_ref={osm_key(e):e for e in elements}
    by_name=defaultdict(list)
    for e in elements:
        if not point(e) or not (station_rank(e) or station_rank(e,'公交')):continue
        for name in native_names(e.get('tags',{})):by_name[name].append(e)
    memberships,relations=build_route_memberships(elements)
    ledger=[]
    for row in rows:
        code=row['code'];name=normalized(row['name']);old_ref=row.get('osm_ref','');e=by_ref.get(old_ref);equivalence=equivalences.get(code)
        if e and not equivalence and name not in native_names(e.get('tags',{})):
            audit['rejected_matches'].append({'code':code,'osm_ref':old_ref,'reason':'referenced object native name differs; no enrichment'})
            e=None
        equivalence=equivalences.get(code)
        if equivalence:
            candidate=by_ref.get(equivalence['osm_ref'])
            if normalized(row['name'])!=normalized(equivalence['native_name']):
                raise ValueError(f'Curated equivalence native label changed: {code}')
            if old_ref and old_ref!=equivalence['osm_ref']:
                raise ValueError(f'Curated equivalence conflicts with a reviewed reference: {code}')
            if not candidate or normalized(equivalence['current_osm_name']) not in native_names(candidate.get('tags',{})):
                raise ValueError(f'Curated equivalence missing or current OSM name changed: {code}')
            if not station_rank(candidate) or not point(candidate):
                raise ValueError(f'Curated equivalence is not a positioned rail station: {code}')
            e=candidate
        if not old_ref and not equivalence:
            kind=source_types.get(code,'')
            candidates=[v for v in by_name[name] if station_rank(v,kind) and (v.get('tags',{}).get('public_transport')!='stop_area' or memberships.get(osm_key(v)) or kind=='BRT')]
            if any(k in kind for k in ('地铁','单轨','轻轨','有轨')):
                candidates=[v for v in candidates if v.get('tags',{}).get('station') in ('subway','light_rail')
                    or v.get('tags',{}).get('subway')=='yes' or v.get('tags',{}).get('railway')=='tram_stop'
                    or memberships.get(osm_key(v))]
            # A unique top-ranked station can coexist with lower-ranked footprint geometry.
            if candidates:
                best=max(station_rank(v,kind) for v in candidates)
                candidates=[v for v in candidates if station_rank(v,kind)==best]
            if len(candidates)==1:
                candidate=candidates[0]
                if row.get('latitude') and metres((float(row['longitude']),float(row['latitude'])),point(candidate))>700:
                    audit['rejected_matches'].append({'code':code,'osm_ref':osm_key(candidate),'reason':'candidate is over 700 m from prior approximate point'})
                else:
                    owners=reference_cities.get(osm_key(candidate),set())
                    if owners and owners!={path.stem}:
                        audit['rejected_matches'].append({'code':code,'osm_ref':osm_key(candidate),'reason':'OSM identity belongs to another city-code group'})
                    else:e=candidate
            elif candidates:
                audit['rejected_matches'].append({'code':code,'reason':'multiple exact station objects','candidates':[osm_key(c) for c in candidates]})
        if not e:
            if not row.get('osm_ref'):
                audit['unresolved'].append({'code':code,'name':row['name'],'reason':'no unique compatible exact OSM station identity'})
            continue
        changes={}
        if not old_ref:
            changes['osm_ref']={'before':'','after':osm_key(e)};row['osm_ref']=osm_key(e)
            p=reviewed_coordinates.setdefault(osm_key(e),point(e))
            reference_cities.setdefault(osm_key(e),set()).add(path.stem)
            for field,value in (('longitude',p[0]),('latitude',p[1])):
                text=str(value)
                if row.get(field,'')!=text:
                    changes[field]={'before':row.get(field,''),'after':text};row[field]=text
        elif not row.get('latitude') and point(e):
            p=reviewed_coordinates.setdefault(osm_key(e),point(e))
            for field,value in (('longitude',p[0]),('latitude',p[1])):
                text=str(value);changes[field]={'before':'','after':text};row[field]=text
        tags=e.get('tags',{})
        if name==normalized(chinese_component(tags)):
            audit['bilingual_name_evidence'].append({'code':code,'osm_ref':osm_key(e),'name':tags['name'],'name:ug':tags['name:ug'],'chinese_component':chinese_component(tags)})
        for field,keys in LANGUAGES.items():
            if row.get(field):continue
            value=next((tags[k].strip() for k in keys if tags.get(k,'')), '')
            if value and normalized(value)!=name:
                changes[field]={'before':'','after':value};row[field]=value
        if changes:
            audit['changes'].update(changes.keys())
            ledger.append({'city_code':path.stem,'code':code,'name':row['name'],'osm_ref':osm_key(e),'source_url':'https://www.openstreetmap.org/'+osm_key(e),'fields':changes,**({'equivalence_sources':equivalence['sources']} if equivalence else {})})
    # Establish line labels by explicit relation membership across multiple station identities.
    grouped=defaultdict(list)
    for row in rows:
        if row.get('line_code'):grouped[row['line_code']].append(row)
    for line,group in grouped.items():
        votes=Counter();seen_refs=set();evidence=defaultdict(set)
        for row in group:
            ref=row.get('osm_ref','')
            if ref in seen_refs:continue
            labels=memberships.get(ref,set())
            if not labels:continue
            seen_refs.add(ref)
            votes.update(labels)
            for label in labels:evidence[label].update(relations[(ref,label)])
        if not votes:continue
        label,count=votes.most_common(1)[0];second=max((v for k,v in votes.items() if k!=label),default=0)
        if count<3 or count<len(seen_refs)*.7 or second>count*.5:continue
        existing={normalized(r.get('line','')) for r in group if r.get('line')}
        if existing and existing!={normalized(label)}:continue
        changed=[]
        for row in group:
            if not row.get('line'):
                row['line']=label;changed.append(row['code']);audit['changes']['line']+=1
                ledger.append({'city_code':path.stem,'code':row['code'],'name':row['name'],'osm_ref':row.get('osm_ref',''),'source_urls':['https://www.openstreetmap.org/relation/'+str(k) for k in sorted(evidence[label])],'fields':{'line':{'before':'','after':label}}})
        if changed:audit['line_evidence'].append({'line_code':line,'label':label,'supporting_station_identities':count,'mapped_station_identities':len(seen_refs),'next_candidate_support':second,'relation_ids':sorted(evidence[label]),'rows_filled':len(changed)})
    audit['changes']=dict(audit['changes'])
    audit['unmatched_after']=sum(not r.get('osm_ref') for r in rows)
    write_csv(path,rows,original)
    return audit,ledger


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--source-types',type=Path)
    parser.add_argument('--city-relations',type=Path)
    parser.add_argument('--equivalences',type=Path)
    parser.add_argument('--audit',type=Path,help='Local detailed change ledger; defaults to research/local (not a station source).')
    args=parser.parse_args()
    types={}
    if args.source_types:
        source=json.loads(args.source_types.read_text())
        types={code:r.get('type','') for code,r in source.get('stations',{}).items()}
    equivalences={r['code']:r for r in json.loads(args.equivalences.read_text())['entries']} if args.equivalences else {}
    reviewed_coordinates={};reference_cities=defaultdict(set)
    for path in sorted((args.root/'data/t-union/stations').glob('*.csv')):
        _,rows=read_csv(path)
        for row in rows:
            if row.get('osm_ref'):
                reference_cities[row['osm_ref']].add(path.stem)
                if row.get('latitude'):
                    position=(float(row['longitude']),float(row['latitude']))
                    if row['osm_ref'] in reviewed_coordinates and reviewed_coordinates[row['osm_ref']]!=position:
                        raise ValueError(f'Baseline coordinates disagree for {row["osm_ref"]}')
                    reviewed_coordinates[row['osm_ref']]=position
    results=[];ledger=[]
    for path in sorted((args.root/'data/t-union/stations').glob('*.csv')):
        result,changes=enrich_city(path,args.cache,types,reviewed_coordinates,reference_cities,equivalences);results.append(result);ledger.extend(changes)
    if args.city_relations:
        registry=args.root/'data/t-union/cities.csv'
        original,rows=read_csv(registry)
        verified={r['code']:r for r in json.loads(args.city_relations.read_text())['verified']}
        for row in rows:
            source=verified.get(row['code'])
            if source:
                for key in ('osm_ref','name_en','name_ja','name_zh_hant'):
                    if not row.get(key) and source.get(key) and normalized(source[key])!=normalized(row['name']):row[key]=source[key]
        write_csv(registry,rows,original)
    output={'checked_date':'2026-10-28','policy':'Exact city-scoped OSM identities with whitespace/parenthesis equivalence or a Chinese component followed by the exact explicit name:ug suffix; preserve primary names/codes; no inferred card codes; line labels require explicit relation membership at multiple station identities.','cities':results,'changes':ledger}
    audit_path=args.audit or args.root/'research/local/china-osm-audit-2026-10-28.json'
    audit_path.parent.mkdir(parents=True,exist_ok=True)
    audit_path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cities':len(results),'snapshot_cities':sum(bool(r['snapshot']) for r in results),'changed_fields':dict(sum((Counter(r['changes']) for r in results),Counter())),'rows_with_changes':len({r['code'] for r in ledger})},ensure_ascii=False))


if __name__=='__main__':main()
