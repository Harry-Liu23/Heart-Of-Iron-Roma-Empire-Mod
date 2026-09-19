"""Reproducible content builder. Reads the installed game, writes only this mod.

Run: python tools/build_mod.py --game <HOI4 directory>
The manifest and reference document are generated from the same focus data.
"""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--game', type=Path, required=True)
args = parser.parse_args()
GAME = args.game
LOC, FOCUSES, DECISIONS, EVENTS, IDEAS, EFFECTS = {}, [], [], [], {}, {}

def write(path, text, bom=False):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('\n'.join(line.rstrip() for line in text.rstrip().splitlines()) + '\n', encoding='utf-8-sig' if bom else 'utf-8')

def read(path):
    return (GAME / path).read_text(encoding='utf-8-sig')

def block_end(s, start):
    """Find matching brace, ignoring quoted strings and comments."""
    depth, quote, comment, escape = 0, False, False, False
    for i in range(start, len(s)):
        c = s[i]
        if comment:
            if c == '\n': comment = False
            continue
        if quote:
            if escape: escape = False
            elif c == '\\': escape = True
            elif c == '"': quote = False
            continue
        if c == '#': comment = True
        elif c == '"': quote = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i + 1
    raise ValueError('Unbalanced block')

def get_block(s, key):
    m = re.search(r'(?m)^\s*' + re.escape(key) + r'\s*=\s*\{', s)
    if not m: raise ValueError(key)
    a = s.index('{', m.start())
    return s[a+1:block_end(s, a)-1]

BASE = read('common/national_focus/greece.txt')
VANILLA = {}
for m in re.finditer(r'(?m)^\s*focus\s*=\s*\{', BASE):
    a = BASE.index('{', m.start())
    chunk = BASE[m.start():block_end(BASE, a)]
    fid = re.search(r'\bid\s*=\s*(\w+)', chunk).group(1)
    VANILLA[fid] = chunk

def loc(key, text):
    LOC[key] = text
    return key

def fid(key):
    return key if key.startswith(('RR_', 'GRE_')) else 'RR_' + key

def done(key): return f'has_completed_focus = {fid(key)}'
def flag(key): return f'has_country_flag = RR_{key}'
def setflag(key): return f'set_country_flag = RR_{key}'
def idea(key): return f'add_ideas = RR_{key}'
def timed(key, days): return f'add_timed_idea = {{ idea = RR_{key} days = {days} }}'

def spirit(key, name, mods, desc=None):
    IDEAS['RR_' + key] = mods
    loc('RR_' + key, name)
    loc('RR_' + key + '_desc', desc or name + '。具体修正见下方数值。')

def tier_effect(name, tiers):
    for tier in tiers:
        branches = []
        for old in tiers:
            if old == tier: continue
            branches.append(('if' if not branches else 'else_if') + ' = { limit = { has_idea = RR_' + old + ' } swap_ideas = { remove_idea = RR_' + old + ' add_idea = RR_' + tier + ' } }')
        EFFECTS['RR_set_' + tier] = '\n'.join(branches) + '\nelse_if = { limit = { NOT = { has_idea = RR_' + tier + ' } } ' + idea(tier) + ' }'

def focus(key, name, group, xy, parents=(), days=35, reward='', summary='', available='', bypass='', mutex=()):
    f = dict(id=fid(key), name=name, group=group, x=xy[0], y=xy[1], days=days,
             parents=[([fid(x) for x in p] if isinstance(p, tuple) else [fid(p)]) for p in parents],
             reward=reward, summary=summary, available=available, bypass=bypass,
             mutex=[fid(x) for x in mutex])
    FOCUSES.append(f)
    loc(f['id'], name)
    loc(f['id'] + '_desc', summary or name + '，使复兴从承诺成为现实。')
    return f

def decision(key, name, cost, days, visible, available, reward, summary, once=True, start='', remove_trigger='', cooldown=0):
    d = dict(id=fid(key), name=name, cost=cost, days=days, visible=visible, available=available,
             reward=reward, summary=summary, once=once, start=start, remove_trigger=remove_trigger, cooldown=cooldown)
    DECISIONS.append(d)
    loc(d['id'], name); loc(d['id']+'_desc', summary)

def event(num, title, body, options):
    e = dict(id=f'rr.{num}', title=title, body=body, options=options)
    EVENTS.append(e)
    loc(f'rr.{num}.t', title); loc(f'rr.{num}.d', body)
    for i, o in enumerate(options): loc(f'rr.{num}.{i}', o[0])

def buildings(state, kind, n, slots=0):
    return f'''{state} = {{ if = {{ limit = {{ is_owned_by = ROOT is_controlled_by = ROOT }}
        add_extra_state_shared_building_slots = {slots}
        add_building_construction = {{ type = {kind} level = {n} instant_build = yes }} }} }}'''

def own(states):
    return '\n'.join(f'{s} = {{ is_owned_by = ROOT is_controlled_by = ROOT }}' for s in states)

def cores(states): return '\n'.join(f'{s} = {{ add_core_of = ROOT }}' for s in states)

def bonus(category, n=1, amount=.5):
    if category == 'engineering': category = 'industry'
    if category == 'production': category = 'cat_production'
    return f'add_tech_bonus = {{ name = RR_research_bonus bonus = {amount} uses = {n} category = {category} }}'

def wargoal(tag, kind='annex_everything', days=365):
    return f'''if = {{ limit = {{ {tag} = {{ exists = yes NOT = {{ is_in_faction_with = ROOT }} NOT = {{ is_subject_of = ROOT }} }} }}
        create_wargoal = {{ type = {kind} target = {tag} expire = {days} }} }}'''

def regional_goal(states):
    ids = ' '.join(f'owns_state = {s}' for s in states)
    return f'''every_other_country = {{ limit = {{ OR = {{ {ids} }} NOT = {{ is_in_faction_with = ROOT }} NOT = {{ is_subject_of = ROOT }} }}
        ROOT = {{ create_wargoal = {{ type = annex_everything target = PREV expire = 365 }} }} }}'''

# Freeze territorial sets from 1936 history, rather than from mutable wartime cores.
STATE_SETS = {t: [] for t in ['TUR', 'BUL', 'ALB', 'YUG', 'ROM', 'ITA']}
for p in (GAME/'history/states').glob('*.txt'):
    s = p.read_text(encoding='utf-8-sig')
    n = re.search(r'\bid\s*=\s*(\d+)', s)
    owner = re.search(r'\bowner\s*=\s*(\w+)', s)
    if n and owner and owner.group(1) in STATE_SETS:
        STATE_SETS[owner.group(1)].append(int(n.group(1)))
TURKEY = sorted(STATE_SETS['TUR'])
# Edirne, Istanbul, Izmit, Bursa, Izmir: Turkish Europe and Aegean coast.
AEGEAN = [797, 341, 347, 340, 339]
LEVANT = [554, 553, 454, 455]
EGYPT = [447, 446, 452, 453, 456]
ITALY = [s for s in STATE_SETS['ITA'] if s in range(2, 200) and s not in [164]]

# Persistent ideas use replacement tiers; transient ideas never enter final totals.
for t, v in [('movement1', .03), ('movement2', .05), ('movement3', .08), ('movement4', .12)]:
    spirit(t, '帝国运动', {'empire_drift':v})
tier_effect('movement', ['movement1','movement2','movement3','movement4'])
spirit('consensus','复兴共识',{'war_support_factor':.05})
spirit('administration','帝国行政',{'political_power_gain':.25})
spirit('vote_mandate','公投授权',{'political_power_factor':.05,'stability_factor':.05})
spirit('purge','整肃余波',{'political_power_factor':-.1,'industrial_capacity_factory':-.05})
spirit('order','秩序重建',{'political_power_gain':.1,'stability_factor':.05,'war_support_factor':.05})
spirit('census','帝国人口普查',{'conscription_factor':.1,'mobilization_speed':.15})
spirit('citizens','统一帝国公民身份',{'conscription_factor':.2,'mobilization_speed':.15})
spirit('martyrs','铭记安纳托利亚灾厄',{'conscription_factor':.1,'war_support_factor':.05})
spirit('wisdom','先贤与雅典的智慧',{'stability_factor':.05,'research_speed_factor':.05})
spirit('culture','希腊先贤与帝国兵法',{'stability_factor':.1,'research_speed_factor':.05,'army_core_defence_factor':.05,'command_power_gain_mult':.05})
spirit('cultural_debate','文化复兴讨论',{'political_power_gain':.2})
spirit('first_war','光复战争动员',{'conscription_factor':.05,'army_core_defence_factor':.05})
spirit('senate','罗马元老议会',{'political_power_factor':.05})
spirit('provincial1','新时代军区',{'political_power_gain':.1})
spirit('provincial2','行省议会',{'political_power_gain':.15})
for t, pp, st, research, manpower in [('central',.30,.05,.03,0),('central_final',.35,.05,.03,0),('pronoia',.15,.1,0,.15),('pronoia_final',.2,.1,0,.15)]:
    spirit(t,'帝国制度：'+('中央集权军区制' if t.startswith('central') else '新普罗尼亚体系'),{'political_power_gain':pp,'stability_factor':st,'research_speed_factor':research,'conscription_factor':manpower})
tier_effect('provinces',['provincial1','provincial2','central','central_final','pronoia','pronoia_final'])
spirit('legal_order','东方帝国秩序',{'laws_cost':-.05,'political_advisor_cost_factor':-.05})
for i, (mp, st, ws, rs) in enumerate([(.05,.05,.05,-.03),(.15,.1,.1,-.05),(.25,.15,.15,-.08),(.35,.2,.2,-.1)],1):
    spirit(f'church{i}','教会与帝国',{'conscription_factor':mp,'stability_factor':st,'war_support_factor':ws,'research_speed_factor':rs})
tier_effect('church',[f'church{i}' for i in range(1,5)])
for i, (mp, st, ws, rs) in enumerate([(0,-.05,-.1,0),(.05,0,-.05,.03),(.15,.1,.05,.06),(.25,.15,.1,.1)],1):
    spirit(f'identity{i}','认同的转变',{'conscription_factor':mp,'stability_factor':st,'war_support_factor':ws,'research_speed_factor':rs})
tier_effect('identity',[f'identity{i}' for i in range(1,5)])
spirit('mare','我们的海',{'industrial_capacity_dockyard':.05})
spirit('rome','重建罗马帝国',{'political_power_gain':.15,'stability_factor':.05,'conscription_factor':.1})
for i, v in [(1,.03),(2,.05),(3,.07),(4,.1)]: spirit(f'science{i}','帝国科研体系',{'research_speed_factor':v})
tier_effect('science',[f'science{i}' for i in range(1,5)])
spirit('education','国家教育体系',{'research_speed_factor':.03},'科研速度+3%；每月稳定度增长0.1个百分点。')
spirit('facilities','实验设施管理局',{'production_speed_facility_factor':.2})
spirit('committee','专项研究委员会',{'special_project_speed_factor':.15})
spirit('scientists','科学家培养计划',{'scientist_research_bonus_factor':.1,'scientist_breakthrough_bonus_factor':.1})
spirit('enterprise_office','帝国企业总局',{'industrial_concern_cost_factor':-.25})
spirit('standards','工业标准化',{'production_factory_efficiency_gain_factor':.05})
spirit('industrial_union','帝国工业联合体',{'industrial_capacity_factory':.03,'production_factory_max_efficiency_factor':.05})

# Politics. Original entry focuses stay available; the custom route starts at x=60.
focus('empire','帝国派登场','政治',(66,2),[('GRE_metaxism_focus','GRE_bring_home_the_exiled_republicans')],70,
      'add_political_power = 100 add_stability = .1 RR_set_movement1 = yes RR_recruit_court = yes add_to_variable = { GRE_monarchist_loyalty = 1 }',
      '政治点+100，稳定度+10；帝国倾向每日+0.03；开放君士坦丁十一世、14名指挥官与帝国顾问。',mutex=['GRE_compromise_with_the_monarchists','GRE_reevaluating_the_drachma','GRE_four_year_plan'])
focus('programme','帝国复兴纲领','政治',(66,3),['empire'],reward='add_political_power = 75 RR_set_movement2 = yes country_event = { id = rr.1 days = 35 }',summary='政治点+75；帝国倾向升至每日+0.05；国策完成后再等待35天触发帝国问题。')
focus('referendum','帝国公投','政治',(64,4),['programme'],reward='RR_take_power = yes '+timed('vote_mandate',365)+' country_event = { id = rr.2 }',summary='君士坦丁十一世执政；365天：政治点获取+5%、稳定度+5。',available=flag('crown'),mutex=['march'])
focus('march','向雅典进军','政治',(68,4),['programme'],reward='RR_take_power = yes add_stability = -.1 '+timed('purge',180)+' country_event = { id = rr.3 days = 180 }',summary='君士坦丁十一世执政；稳定度−10；180天整肃余波：政治点获取−10%、工厂产出−5%，期满事件给予365天秩序重建。',available=flag('basileus'),mutex=['referendum'])
focus('government','帝国政府','政治',(66,5),[('referendum','march')],reward='add_political_power = 150 RR_emperor_administration = yes',summary='政治点+150；皇帝追加每日政治点+0.15；开放行政、科研和顾问。')
focus('codex','重订罗马法典','政治',(65,6),['government'],reward=setflag('jurist'),summary='开放大法官：任用时法律与政治顾问成本−15%、意识形态变化抵制+25%。',available=flag('senate_rebuilt'))
focus('citizenship','统一帝国公民身份','政治',(66,7),['codex'],reward='remove_ideas = RR_census '+idea('citizens')+' RR_set_movement4 = yes',summary='人口普查精神升级为适役人口系数+20%、动员速度+15%；帝国倾向每日+0.12。',available=flag('census_done'))
focus('authority','恢复帝国权威','政治',(66,8),['citizenship'],reward='add_political_power = 100 '+idea('administration'),summary='政治点+100；每日政治点+0.25；确立自主外交，不依附外国领导的阵营。')

focus('memory','铭记安纳托利亚灾厄','文化',(59,3),['empire'],reward=idea('martyrs'),summary='适役人口系数+10%，战争支持度+5。')
focus('wisdom_focus','先贤与雅典的智慧','文化',(59,4),['memory'],reward=idea('wisdom')+' '+timed('cultural_debate',600),summary='稳定度+5、科研速度+5%；600天每日政治点+0.20。')
focus('warrior_culture','底比斯与马其顿的兵法','文化',(59,5),['wisdom_focus'],reward='remove_ideas = RR_wisdom '+idea('culture'),summary='文化精神升级为稳定度+10、科研+5%、核心防御+5%、指挥点增长+5%。')
focus('jewel','拜占庭掌上明珠','文化',(59,6),['warrior_culture'],reward=setflag('capital_unlocked'),summary='开放25政治点迁都君士坦丁堡决议；不触发土耳其交涉事件。')

focus('legitimacy','宣称拜占庭正统','第一次光复',(73,4),['programme'],reward=setflag('turkey_diplomacy'),summary='开放对土交涉决议：75政治点，1937年1月1日起可用。')
focus('new_rome','新罗马再临','第一次光复',(73,5),['legitimacy'],reward='set_cosmetic_tag = RR_BYZ '+cores(TURKEY)+' country_event = { id = rr.7 }',summary='国名改为拜占庭；获得全部1936年土耳其本土地块的核心。',available=own([797]))
focus('unify_homeland','完成故土统一','第一次光复',(73,6),['new_rome'],reward='if = { limit = { TUR = { exists = yes } } create_wargoal = { type = take_core_state target = TUR expire = 180 } }',summary='获得对土耳其180天收复核心战争目标；已统一全部故土则跳过。',bypass=own(TURKEY))
focus('diplomatic_order','帝国的外交秩序','第一次光复',(76,6),['new_rome'],reward='set_rule = { can_create_factions = yes } if = { limit = { is_in_faction = no is_subject = no } create_faction = RR_imperial_concord }',summary='独立且未加入阵营时建立“帝国协约”。')
focus('great_restoration','准备伟大光复','第一次光复',(71,9),['authority','new_rome'],70,'add_political_power = 150','政治点+150；完成制度改革并统一土耳其故土后，开放后续制度、宗教和征服分支。',available=own(TURKEY))

focus('themes','新时代军区','安纳托利亚制度',(62,10),['great_restoration'],reward='add_political_power = 75 RR_set_provincial1 = yes',summary='政治点+75；行省行政每日政治点+0.10；开放可选行省议会决议。')
focus('eastern_empire','东方帝国复兴','安纳托利亚制度',(62,11),['themes'],reward=idea('legal_order'),summary='法律与政治顾问成本−5%；开放制度会议决议。')
focus('constitution','帝国宪制确立','安纳托利亚制度',(62,12),['eastern_empire'],reward='if = { limit = { has_country_flag = RR_central } RR_set_central_final = yes } else = { RR_set_pronoia_final = yes } RR_end_instability = yes country_event = { id = rr.12 }',summary='中央制每日政治点最终+0.35，普罗尼亚制最终+0.20；政局动荡替换为罗马元老议会，政治点获取+5%。',available='OR = { '+flag('central')+' '+flag('pronoia')+' }')
focus('faith','帝国与信仰','宗教',(68,10),['great_restoration'],reward='add_political_power = 75',summary='政治点+75；选择教会帝国或公民认同路线。')
for i,(key,name,days) in enumerate([('church_crown','教会与皇权',35),('dioceses','复兴教区网络',70),('faith_guard','信仰的守护者',70),('sacred_contract','神圣帝国契约',70)],1):
    focus(key,name,'宗教：教会',(66,10+i),['faith' if i==1 else ['church_crown','dioceses','faith_guard'][i-2]],days,f'RR_set_church{i} = yes',f'教会与帝国升级至第{i}档：'+['适役人口+5%、稳定度+5、战争支持+5、科研−3%。','适役人口+15%、稳定度+10、战争支持+10、科研−5%。','适役人口+25%、稳定度+15、战争支持+15、科研−8%。','适役人口+35%、稳定度+20、战争支持+20、科研−10%。'][i-1],mutex=['private_faith'] if i==1 else [])
focus('private_faith','信仰属于私人','宗教：公民',(70,11),['faith'],reward='RR_set_identity1 = yes',summary='认同的转变：稳定度−5、战争支持−10；开放公民教育改革决议。',mutex=['church_crown'])
focus('roman_community','罗马人的共同体','宗教：公民',(70,12),['private_faith'],70,'RR_set_identity3 = yes','认同精神升级：稳定度+10、战争支持+5、科研+6%、适役人口系数+15%。',available=flag('civic_education'))
focus('citizen_above_creed','公民高于教籍','宗教：公民',(70,13),['roman_community'],reward='RR_set_identity4 = yes',summary='认同精神最终：稳定度+15、战争支持+10、科研+10%、适役人口系数+25%。')

focus('balkan_rights','巴尔干的帝国权利','战争：巴尔干',(75,10),['great_restoration'],reward='\n'.join(wargoal(t) for t in ['BUL','ALB','YUG','ROM']),summary='一次性获得对仍存在的保加利亚、阿尔巴尼亚、南斯拉夫、罗马尼亚365天吞并战争目标。',bypass='BUL = { exists = no } ALB = { exists = no } YUG = { exists = no } ROM = { exists = no }')
BALKANS = sorted(set(sum([STATE_SETS[t] for t in ['BUL','ALB','YUG','ROM']],[])))
focus('balkan_provinces','重建巴尔干行省','战争：巴尔干',(75,11),['balkan_rights'],70,cores(BALKANS)+buildings(47,'industrial_complex',2,2),'整合巴尔干固定故土地块为核心；希腊本土+2民工、2槽。',available=own(BALKANS))
focus('taurus','打开托罗斯山门','战争：黎凡特',(80,10),['great_restoration'],reward=regional_goal([554,553]),summary='获得对北叙利亚目标地区当前外国拥有者的365天吞并战争目标。')
focus('antioch','重返安条克','战争：黎凡特',(80,11),['taurus'],reward='add_political_power = 50 '+cores([554,553])+regional_goal([454,455]),summary='政治点+50；北叙利亚整合核心；开放南方目标及圣城守护者决议。',available=own([554,553]))
focus('alexandria','亚历山大里亚再临','战争：埃及',(84,11),['great_restoration'],reward=cores(EGYPT)+buildings(447,'industrial_complex',1,1),summary='整合埃及目标地区为核心；亚历山大地区+1民工、1槽。不要求先完成粮仓决议。',available=own(EGYPT))
focus('avenge_1204','洗雪1204','战争：意大利',(74,12),['balkan_provinces'],reward='add_war_support = .05 '+wargoal('ITA'),summary='战争支持度+5；对意大利365天吞并战争目标。',mutex=['western_crown'])
focus('western_crown','西部帝冠','战争：意大利',(77,12),['balkan_provinces'],reward='add_political_power = 75 if = { limit = { ITA = { exists = yes } } ITA = { country_event = { id = rr.20 } } }',summary='政治点+75；向意大利提出帝冠协定，拒绝后获得战争目标。',mutex=['avenge_1204'])
focus('italy_return','重返意大利','战争：意大利',(75,13),[('avenge_1204','western_crown')],reward='add_army_experience = 25 '+cores(ITALY),summary='陆军经验+25；拥有意大利本土后整合为核心。',available=own(ITALY))
focus('two_romes','旧罗马与新罗马','战争：意大利',(75,14),['italy_return'],reward='add_stability = .05',summary='稳定度+5；要求拥有并控制罗马与君士坦丁堡。',available=own([2,797]))
focus('anti_democracy','向共和宣战','战争：意识形态',(72,15),['two_romes'],reward='\n'.join(f'if = {{ limit = {{ {t} = {{ has_government = democratic }} }} '+wargoal(t,'topple_government')+' }' for t in ['ENG','FRA']),summary='对民主英国、法国取得365天推翻政府战争目标；与反法西斯、反共产两线互斥。',mutex=['anti_fascism','anti_communism'])
focus('anti_fascism','向法西斯宣战','战争：意识形态',(75,15),['two_romes'],reward='if = { limit = { GER = { has_government = fascism } } '+wargoal('GER','topple_government')+' }',summary='对法西斯德国取得365天推翻政府战争目标。',mutex=['anti_democracy'])
focus('anti_communism','向共产宣战','战争：意识形态',(78,15),['two_romes'],reward='if = { limit = { SOV = { has_government = communism } } '+wargoal('SOV')+' } every_other_country = { limit = { has_government = communism is_neighbor_of = SOV NOT = { is_in_faction_with = ROOT } NOT = { is_subject_of = ROOT } } ROOT = { create_wargoal = { type = annex_everything target = PREV expire = 365 } } }',summary='对共产主义苏联及其陆地邻接共产国家取得365天吞并战争目标。',mutex=['anti_democracy'])
focus('restore_rome','重建罗马帝国','罗马终点',(80,16),['two_romes'],70,idea('rome'),'每日政治点+0.15、稳定度+5、适役人口系数+10%；开放一次性国号与首都决议。',available=flag('mare_done')+' '+own(ITALY+TURKEY+BALKANS+LEVANT+EGYPT))

for module in ['content_economy.py', 'content_events.py', 'content_people.py', 'content_fixes.py', 'content_balance.py', 'content_ingame_fixes.py', 'content_army.py', 'emit_mod.py']:
    exec(compile((ROOT/'tools'/module).read_text(encoding='utf-8-sig'), module, 'exec'), globals())



