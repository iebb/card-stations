from __future__ import annotations
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'research/enrich_china.py'
SPEC=importlib.util.spec_from_file_location('china_enrichment',SCRIPT)
module=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(module)


class ChinaEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.cache=self.root/'cache';self.cache.mkdir()
        self.path=self.root/'1000.csv'

    def write(self,rows,elements):
        columns=['code','name','line_code','line','latitude','longitude','osm_ref']
        with self.path.open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
        (self.cache/'1000.json').write_text(json.dumps({'elements':elements,'osm3s':{'timestamp_osm_base':'2026-10-28T00:00:00Z'}}))

    def read(self):
        with self.path.open() as handle:return list(csv.DictReader(handle))

    def row(self,code='10000101',name='测试站',ref='',line=''):
        return {'code':code,'name':name,'line_code':'100001','line':line,'latitude':'','longitude':'','osm_ref':ref}

    def station(self,key=1,name='测试站',lon=116.4,lat=39.9):
        return {'type':'node','id':key,'lon':lon,'lat':lat,'tags':{'name':name,'name:en':'Test Station','railway':'station','station':'subway'}}

    def run_enrich(self,positions=None,owners=None):
        return module.enrich_city(self.path,self.cache,{'10000101':'地铁'},positions or {},owners or {},{})

    def test_new_alias_uses_existing_reviewed_reference_coordinates(self):
        self.write([self.row()],[self.station()])
        self.run_enrich({'node/1':(116.400001,39.900001)},{'node/1':{'1000'}})
        row=self.read()[0]
        self.assertEqual((row['longitude'],row['latitude']),('116.400001','39.900001'))
        self.assertEqual((row['code'],row['name']),('10000101','测试站'))

    def test_other_city_reference_is_not_reused(self):
        self.write([self.row()],[self.station()])
        audit,_=self.run_enrich(owners={'node/1':{'1121'}})
        self.assertFalse(self.read()[0].get('osm_ref'))
        self.assertIn('another city',audit['rejected_matches'][0]['reason'])

    def test_ambiguous_station_identity_is_not_guessed(self):
        self.write([self.row()],[self.station(),self.station(2,lon=116.42)])
        self.run_enrich()
        self.assertFalse(self.read()[0].get('osm_ref'))

    def test_bilingual_chinese_component_requires_exact_tagged_suffix(self):
        tags={'name':'三屯碑 سەندۈڭبىي','name:ug':'سەندۈڭبىي\u200e'}
        self.assertEqual(module.chinese_component(tags),'三屯碑')
        self.assertIn('三屯碑',module.native_names(tags))
        tags['name:ug']='different'
        self.assertFalse(module.chinese_component(tags))

    def test_bilingual_rule_rejects_partial_or_untagged_names(self):
        for tags in ({'name':'三屯碑 سەندۈڭبىي'}, {'name':'三屯碑新区 سەندۈڭبىي','name:ug':'سەندۈڭبىي'}, {'name':'三屯碑سەندۈڭبىي','name:ug':'سەندۈڭبىي'}):
            self.assertNotIn('三屯碑',module.native_names(tags))

    def test_empty_role_track_way_cannot_create_station_route_vote(self):
        station=self.station()
        area={'type':'relation','id':10,'tags':{'public_transport':'stop_area','name':'测试站'},'members':[{'type':'node','ref':1,'role':'station'},{'type':'way','ref':5,'role':''}]}
        route={'type':'relation','id':20,'tags':{'type':'route','route':'subway','ref':'7'},'members':[{'type':'way','ref':5,'role':''}]}
        membership,_=module.build_route_memberships([station,area,route])
        self.assertFalse(membership.get('node/1'))
        route['members'][0]['role']='stop'
        membership,_=module.build_route_memberships([station,area,route])
        self.assertEqual(membership['node/1'],{'7号线'})

    def test_line_label_comes_from_route_membership_not_card_code_digits(self):
        rows=[self.row(code=f'1000010{i}',name=f'站{i}',ref=f'node/{i}') for i in range(1,4)]
        elements=[self.station(i,name=f'站{i}',lon=116.4+i*.001) for i in range(1,4)]
        elements.append({'type':'relation','id':20,'tags':{'type':'route','route':'subway','ref':'7'},'members':[{'type':'node','ref':i,'role':'stop'} for i in range(1,4)]})
        self.write(rows,elements);audit,_=self.run_enrich()
        self.assertEqual({r['line'] for r in self.read()},{'7号线'})
        self.assertEqual(audit['line_evidence'][0]['relation_ids'],[20])

    def test_existing_line_conflict_blocks_group_fill(self):
        rows=[self.row(code=f'1000010{i}',name=f'站{i}',ref=f'node/{i}',line='1号线' if i==1 else '') for i in range(1,4)]
        elements=[self.station(i,name=f'站{i}',lon=116.4+i*.001) for i in range(1,4)]
        elements.append({'type':'relation','id':20,'tags':{'type':'route','route':'subway','ref':'7'},'members':[{'type':'node','ref':i,'role':'stop'} for i in range(1,4)]})
        self.write(rows,elements);self.run_enrich()
        self.assertEqual([r.get('line','') for r in self.read()],['1号线','',''])


if __name__=='__main__':unittest.main()
