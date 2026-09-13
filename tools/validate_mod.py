
"""Static content and design regression checks; not a substitute for a game session."""
from pathlib import Path
import argparse,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);args=p.parse_args();GAME=args.game
manifest=json.loads((ROOT/'docs/content_manifest.json').read_text(encoding='utf-8'))
failures=[];checks=0
def check(condition,message):
    global checks
    checks+=1
    if not condition:failures.append(message)
TOKEN=re.compile(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]|[^\s{}]+')
def balanced(s,label):
    depth=0
    for m in TOKEN.finditer(s):
        t=m.group()
        if t.startswith(('"','#')):continue
        if t=='{':depth+=1
        elif t=='}':depth-=1
        if depth<0:break
    check(depth==0,label+' braces')
def text(p):return p.read_text(encoding='utf-8-sig')
paths=[p for folder in ['common','events'] for p in (ROOT/folder).rglob('*.txt')]
for path in paths:balanced(text(path),str(path.relative_to(ROOT)))
for path in (ROOT/'localisation').rglob('*.yml'):
    check(path.read_bytes().startswith(b'\xef\xbb\xbf'),str(path)+' BOM')
focuses={f['id']:f for f in manifest['focuses']}
check(len(focuses)==len(manifest['focuses']),'duplicate custom focus IDs')
base=(ROOT/'common/national_focus/greece.txt').read_text(encoding='utf-8')
all_focus_ids=re.findall(r'\bid\s*=\s*((?:GRE|RR)_\w+)',base)
# A vanilla fake leader id is numeric, so excluded.
check(len(all_focus_ids)==len(set(all_focus_ids)),'duplicate focus IDs in integrated tree')
for f in focuses.values():
    for group in f['parents']:
        for parent in group:check(parent in all_focus_ids,f['id']+' missing parent '+parent)
    for other in f['mutex']:
        check(other in all_focus_ids,f['id']+' missing mutex '+other)
        if other in focuses:check(f['id'] in focuses[other]['mutex'],f['id']+' asymmetric mutex '+other)
seen=set();visiting=set()
def visit(k):
    if k in seen:return
    if k in visiting:failures.append('cycle '+k);return
    visiting.add(k)
    for group in focuses[k]['parents']:
        for other in group:
            if other in focuses:visit(other)
    visiting.remove(k);seen.add(k)
for k in focuses:visit(k)
check(len(seen)==len(focuses),'focus graph not fully traversed')
check(len(manifest['commanders'])==14,'14 commanders required')
check(sum(x[4] for x in manifest['commanders'])==2,'2 marshals required')
for x in manifest['commanders']:check(2<=x[2]<=4,'commander skill too high')
for k in ['RR_farmers','RR_bulk_debt','RR_fiscal','RR_autarky','RR_tobacco','RR_mining','RR_tourism','RR_mobilize_economy','RR_athens','RR_islands','RR_slums','RR_monopolies','RR_lignite','RR_soil','RR_farmlands']:
    check(focuses[k]['days']==35,k+' must be 35 days')
for k in ['RR_facility_office','RR_research_committee','RR_scientist_training']:check(focuses[k]['days']==14,k+' must be 14 days')
check('days = 35' in focuses['RR_programme']['reward'],'issue must occur 35 days AFTER focus')
check('GRE_the_kings_government' not in focuses['RR_empire']['parents'],'removed king prerequisite')
check(focuses['RR_great_restoration']['parents']==[['RR_authority'],['RR_new_rome']],'great restoration AND gate')
check('RR_anti_democracy' not in focuses['RR_anti_fascism']['parents'],'anti ideology graph')
check('RR_anti_communism' not in focuses['RR_anti_fascism']['mutex'],'fascism and communism may both be taken')
dec={d['id']:d for d in manifest['decisions']}
d=dec['RR_turkey_demand']
check(d['cost']==75 and '1936.12.31' in d['available'],'Turkish demand date/cost')
check('has_war_support' not in d['available'] and 'has_stability' not in d['available'],'extra Turkish demand gates')
check(dec['RR_national_laboratory']['days']==180,'lab decision duration')
check(dec['RR_holy_city']['cost']==0 and dec['RR_holy_city']['days']==0,'holy city immediate/free')
check(dec['RR_granary']['days']==7,'granary 7 days')
check(dec['RR_our_sea']['days']==30,'our sea 30 days')
for f in focuses.values():
    check('RR_national_laboratory_taken' not in f['available'],'lab must not gate focuses')
event={e['id']:e for e in manifest['events']}
check([o[2] for o in event['rr.5']['options']]==[90,10],'Turkey 90/10')
check('declare_war_on' in event['rr.5']['options'][0][1],'rejection immediate war')
check('country_event' not in focuses['RR_jewel']['reward'],'jewel must not issue Turkey demand')
check(manifest['ideas']['RR_church4']['conscription_factor']==.35,'church final manpower')
check(manifest['ideas']['RR_identity4']['conscription_factor']==.25,'civic final manpower')
check(manifest['ideas']['RR_senate']['political_power_factor']==.05,'senate +5% PP')
effects=text(ROOT/'common/scripted_effects/rr_effects.txt')
check('amount_research_slots < 6' in effects,'research slots cap')
check(sum('RR_research_slot = yes' in f['reward'] for f in focuses.values())==3,'three science-slot awards')
# All declared modifiers must be real engine modifiers, or documented generated ones.
doc=text(GAME/'documentation/modifiers_documentation.md')
known=set(re.findall(r'^## (\w+)\s*$',doc,re.M))
game_ideas='\n'.join(text(p) for p in (GAME/'common/ideas').glob('*.txt'))
game_traits=text(GAME/'common/country_leader/00_traits.txt')
for data in [manifest['ideas'],manifest['traits']]:
    for name,mods in data.items():
        for key in mods:
            check(key in known or re.search(r'\b'+re.escape(key)+r'\s*=',game_ideas+game_traits) is not None or key=='empire_drift',f'unknown modifier {name}: {key}')
traits=text(GAME/'common/unit_leader/00_traits.txt')
for key,name,level,tokens,marshal in manifest['commanders']:
    for token in tokens.split():check(re.search(r'(?m)^\s*'+token+r'\s*=',traits) is not None,'unknown general trait '+token)
# State identifiers and referenced custom effects/ideas must resolve.
stateids=set()
for path in (GAME/'history/states').glob('*.txt'):
    m=re.search(r'\bid\s*=\s*(\d+)',text(path))
    if m:stateids.add(int(m.group(1)))
for values in manifest['state_sets'].values():
    for sid in values:check(sid in stateids,'unknown state '+str(sid))
definitions=set()
for path in paths:
    definitions.update(re.findall(r'\b(RR_\w+)\s*=\s*\{',text(path)))
for path in paths:
    for key in re.findall(r'\b(RR_\w+)\s*=\s*yes\b',text(path)):
        check(key in definitions,'undefined scripted effect '+key)
for path in paths:
    for key in re.findall(r'\b(?:add_ideas|remove_ideas|add_idea|remove_idea)\s*=\s*(RR_\w+)',text(path)):
        check(key in definitions,'undefined custom idea '+key)
loc=text(ROOT/'localisation/simp_chinese/rr_content_l_simp_chinese.yml')
locids=set(re.findall(r'(?m)^\s*(\S+):\d* ',loc))
for f in focuses.values():check(f['id'] in locids and f['id']+'_desc' in locids,'missing focus localization')
for d in dec:check(d in locids and d+'_desc' in locids,'missing decision localization')
report={'checks':checks,'failures':failures,'engine_session_tested':False}
(ROOT/'docs/validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(failures))

