
def engine_mods(mods):
    out=dict(mods)
    if 'laws_cost' in out:
        value=out.pop('laws_cost')
        for k in ['economy_cost_factor','trade_laws_cost_factor','mobilization_laws_cost_factor']:out[k]=value
    if 'counter_intelligence' in out:out['intelligence_agency_defense']=out.pop('counter_intelligence')
    return out
for k in IDEAS:IDEAS[k]=engine_mods(IDEAS[k])
for k in TRAITS:TRAITS[k]=engine_mods(TRAITS[k])
write('common/country_leader/rr_traits.txt','leader_traits = {\n'+'\n'.join(k+' = { '+' '.join(f'{m} = {v}' for m,v in mods.items())+' }' for k,mods in TRAITS.items())+'\n}')
EFFECTS['RR_research_slot']='if = { limit = { amount_research_slots < 6 } add_research_slot = 1 }'
EFFECTS['RR_arsenal_funds']='if = { limit = { has_dlc = "Arms Against Tyranny" } mio:RR_mio_piraeus = { add_mio_funds_gain_factor = .1 } }'
write('common/military_industrial_organization/modifiers/rr_modifiers.txt','# Funds use the documented MIO effect; no custom modifier database.')
dyn=(ROOT/'common/dynamic_modifiers/rr_capitals.txt').read_text(encoding='utf-8')
write('common/dynamic_modifiers/rr_capitals.txt',dyn.replace('local_defence =','army_defence_factor ='))
def alter_focus(text,key,transform):return text.replace(VANILLA[key],transform(VANILLA[key]),1)
base=BASE
base=alter_focus(base,'GRE_metaxism_focus',lambda s:re.sub(r'\s*prerequisite = \{ focus = GRE_the_kings_government \}','',s))
for v in VANILLA_MUTEX:
    base=alter_focus(base,v,lambda s:s.replace('id = '+v,'id = '+v+'\n mutually_exclusive = { focus = RR_empire }',1))
# Reciprocal exclusions are defined in content_ingame_fixes.py.
for key,old in VANILLA.items():
    if key in ['GRE_bring_home_the_exiled_republicans','GRE_metaxism_focus','GRE_the_kings_government','GRE_compromise_with_the_monarchists','GRE_reevaluating_the_drachma','GRE_four_year_plan']:continue
    base=re.sub(r'\bid = '+re.escape(key)+r'(?=\s)', 'id = '+key+'\n available = { NOT = { has_completed_focus = RR_empire } }',base,count=1)
def merge_fields(s,field):
    chunks=[]
    for m in list(re.finditer(r'(?m)^\s*'+field+r'\s*=\s*\{',s)):
        a=s.index('{',m.start());end=block_end(s,a)
        prefix=re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*', '', s[:m.start()])
        if prefix.count('{')-prefix.count('}') != 1: continue
        chunks.append((m.start(),end,s[a+1:end-1]))
    if len(chunks)<2:return s
    for start,end,body in reversed(chunks):s=s[:start]+s[end:]
    pos=s.index('{')+1
    return s[:pos]+'\n '+field+' = { '+'\n'.join(x[2] for x in chunks)+' }\n'+s[pos:]
for m in reversed(list(re.finditer(r'(?m)^\s*focus\s*=\s*\{',base))):
    a=base.index('{',m.start());end=block_end(base,a)
    base=base[:m.start()]+merge_fields(merge_fields(base[m.start():end],'available'),'mutually_exclusive')+base[end:]
base=base.replace('add = 10','add = 100',1)
icons={'陆军：步兵':'GFX_goal_generic_army_doctrines','陆军：装甲':'GFX_goal_generic_army_tanks','陆军：合流':'GFX_goal_generic_allies_build_infantry','政治':'GFX_goal_generic_political_pressure','文化':'GFX_goal_generic_national_unity','科研':'GFX_focus_research','实验设施':'GFX_goal_generic_secret_weapon','企业':'GFX_goal_generic_production2'}
focus_text=[]
for f in FOCUSES:
    lines=[f"focus = {{ id = {f['id']}",f"icon = {icons.get(f['group'],'GFX_goal_generic_construct_civ_factory')}",f"x = {f['x']} y = {f['y']} cost = {f['days']/7:g}"]
    for p in f['parents']:lines.append('prerequisite = { '+' '.join('focus = '+x for x in p)+' }')
    if f['mutex']:lines.append('mutually_exclusive = { '+' '.join('focus = '+x for x in f['mutex'])+' }')
    if f['available']:lines.append('available = { '+f['available']+' }')
    if f['bypass']:lines.append('bypass = { '+f['bypass']+' }')
    lines+=['ai_will_do = { base = 2 }','completion_reward = { '+f['reward']+' }','}']
    focus_text.append('\n'.join(lines))
end=base.rfind('}')
write('common/national_focus/greece.txt',base[:end]+'\n'+'\n'.join(focus_text)+'\n'+base[end:])
for p in ['common/national_focus/rr_greece.txt','common/ideas/rr_byzantine_ideas.txt']:
    old=ROOT/p;backup=ROOT/'docs/prototype'/old.name
    if old.exists() and not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(old.read_bytes())
    write(p,'# Superseded by integrated 0.2 content; original archived in docs/prototype.')
write('common/ideas/rr_spirits.txt','ideas = { country = {\n'+'\n'.join(k+' = { allowed = { original_tag = GRE } allowed_civil_war = { always = yes } picture = generic_political_advisor_europe_1 removal_cost = -1 modifier = { '+' '.join(f'{m} = {v}' for m,v in mods.items())+' }'+(' '+IDEA_EXTRA[k] if IDEA_EXTRA.get(k) else '')+' }' for k,mods in IDEAS.items())+'\n} }')

debt_body=get_block(read('common/decisions/GRE.txt'),'GRE_pay_back_debt_to_the_ifc_category')
for a,b in ECON_MAP.items():debt_body=debt_body.replace(a,b)
# Keep the original currency focus as the debt-decision prerequisite.
debt_ids=re.findall(r'(?m)^\s*(GRE_\w+)\s*=\s*\{',debt_body)
for old in debt_ids:
    if old.startswith(('GRE_small_installment','GRE_large_installment','GRE_restructuring_our_debt','GRE_defaulting_on_our_debt')):
        new='RR_debt_'+old[4:]
        debt_body=re.sub(r'\b'+old+r'\b',new,debt_body)
        loc(new,old.replace('GRE_','').replace('_',' '))
        loc(new+'_desc','原版希腊偿债机制。债务进度、费用和等待时间保持原版。')
write('common/decisions/rr_debt.txt','RR_debt_category = {\n'+debt_body+'\n}')
loc('RR_debt_category','帝国财政：国际金融委员会债务')
dec_text=[]
for d in DECISIONS:
    taken=d['id']+'_taken';available=d['available']
    if d['once']:available+=' NOT = { has_country_flag = '+taken+' }'
    start=d['start']+(' set_country_flag = '+taken if d['once'] else '')
    lines=[d['id']+' = { icon = generic_political_discourse fire_only_once = no',f"cost = {d['cost']}",'visible = { '+d['visible']+' }','available = { '+available+' }','ai_will_do = { factor = 1 }']
    if d['days']:
        lines += [f"days_remove = {d['days']}",'complete_effect = { '+start+' }','remove_effect = { '+d['reward']+' }']
        if d['cooldown']:lines.append(f"days_re_enable = {d['cooldown']}")
    else:lines.append('complete_effect = { '+start+' '+d['reward']+' }')
    if d['remove_trigger']:lines.append('remove_trigger = { '+d['remove_trigger']+' }')
    lines.append('}');dec_text.append('\n'.join(lines))
write('common/decisions/rr_decisions.txt','RR_imperial_decisions = {\n'+'\n'.join(dec_text)+'\n}')
write('common/decisions/categories/rr_categories.txt','''RR_imperial_decisions = { icon = generic_political_actions allowed = { original_tag = GRE } visible = { has_completed_focus = RR_empire } }
RR_debt_category = { icon = gre_paying_ifc_debt allowed = { original_tag = GRE has_dlc = "Battle for the Bosporus" } visible = { has_completed_focus = RR_empire has_completed_focus = GRE_reevaluating_the_drachma } }''')
loc('RR_imperial_decisions','帝国复兴事务')
event_text=['add_namespace = rr']
for e in EVENTS:
    lines=[f"country_event = {{ id = {e['id']} title = {e['id']}.t desc = {e['id']}.d",'picture = GFX_report_event_generic_parliament is_triggered_only = yes']
    for i,(title,effect,chance) in enumerate(e['options']):lines.append(f"option = {{ name = {e['id']}.{i} ai_chance = {{ factor = {chance} }} {effect} }}")
    lines.append('}');event_text.append('\n'.join(lines))
write('events/rr_events.txt','\n'.join(event_text))
write('common/scripted_effects/rr_effects.txt','\n'.join(k+' = {\n'+v+'\n}' for k,v in EFFECTS.items()))
write('common/on_actions/rr_on_actions.txt','''on_actions = {
 on_daily_GRE = { effect = {
   if = { limit = { has_completed_focus = RR_tourism } RR_refresh_tourism = yes }
   if = { limit = { has_country_flag = RR_enterprises } RR_update_enterprises = yes }
   if = { limit = { has_idea = RR_first_war NOT = { has_war_with = TUR } } remove_ideas = RR_first_war }
   if = { limit = { has_government = empire is_in_faction = yes is_faction_leader = no } leave_faction = yes }
 }}
 on_monthly_GRE = { effect = { if = { limit = { has_country_flag = RR_education_done } add_stability = .001 } } }
 on_capitulation = { effect = { if = { limit = { FROM = { original_tag = GRE has_government = empire } } FROM = { set_country_flag = RR_victory_pending } } } }
}''')
gre_effects=read('common/scripted_effects/GRE_scripted_effects.txt')
old_body=get_block(gre_effects,'GRE_political_instability_update_effect')
new_body='if = { limit = { NOT = { has_country_flag = RR_constitution_done } } '+old_body+' } else = { add_ideas = RR_senate }'
gre_effects=gre_effects.replace(old_body,new_body,1)
write('common/scripted_effects/GRE_scripted_effects.txt',gre_effects)
write('common/ideologies/rr_empire.txt','''ideologies = { empire = {
 types = { roman_restoration = { can_be_randomly_selected = no } }
 color = { 112 42 130 }
 rules = { can_force_government = yes can_send_volunteers = yes can_puppet = yes }
 war_impact_on_world_tension = 1.0 faction_impact_on_world_tension = 1.0
 modifiers = { justify_war_goal_when_in_major_war_time = -.8 lend_lease_tension = .5 }
 can_collaborate = yes ai_ideology_wanted_units_factor = 1.1
 dynamic_faction_names = { RR_imperial_concord }
} }''')
loc('empire','帝国');loc('empire_noun','帝国');loc('empire_desc','帝国政府')
loc('roman_restoration','罗马复兴主义');loc('roman_restoration_desc','以罗马公民身份、帝国法统和国家复兴为基础的政治运动。')
for tag,name,adj in [('GRE','希腊','希腊'),('RR_BYZ','拜占庭','拜占庭'),('RR_ROM','罗马帝国','罗马')]:
    for suffix in ['','_DEF','_ADJ']:loc(tag+'_empire'+suffix,adj if suffix=='_ADJ' else name)
    if tag!='GRE':
        for ideology_name in ['neutrality','democratic','fascism','communism']:
            for suffix in ['','_DEF','_ADJ']:loc(tag+'_'+ideology_name+suffix,adj if suffix=='_ADJ' else name)
for law_file in ['_manpower.txt','_economic.txt']:
    s=read('common/ideas/'+law_file)
    s=re.sub(r'has_government\s*=\s*fascism',r'OR = { has_government = fascism has_government = empire }',s)
    write('common/ideas/'+law_file,s)
s=read('common/military_industrial_organization/organizations/GRE_organization.txt')
s=s.replace('has_completed_focus = GRE_crack_down_on_foreign_monopolies','OR = { has_completed_focus = GRE_crack_down_on_foreign_monopolies has_completed_focus = RR_monopolies }')
write('common/military_industrial_organization/organizations/GRE_organization.txt',s)
for p in (GAME/'localisation/simp_chinese').glob('*.yml'):
    if 'bftb' not in p.name:continue
    for key,text in re.findall(r'(?m)^\s*(GRE_(?:small_installment|large_installment|restructuring_our_debt|defaulting_on_our_debt)\w*):\d*\s*"(.*)"',p.read_text(encoding='utf-8-sig')):
        LOC['RR_debt_'+key[4:]]=text
for f in FOCUSES:
    LOC[f['id']+'_desc']=f['summary']
for lang in ['simp_chinese','english']:
    lines=['l_'+lang+':']
    for key,value in sorted(LOC.items()):
        value=value.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
        lines.append(f' {key}:0 "{value}"')
    write('localisation/'+lang+'/rr_content_l_'+lang+'.yml','\n'.join(lines),bom=True)
for lang in ['simp_chinese','english']:
    p=ROOT/'localisation'/lang/('rr_focus_l_'+lang+'.yml')
    if p.exists():
        backup=ROOT/'docs/prototype'/p.name
        if not backup.exists():backup.write_bytes(p.read_bytes())
        write(str(p.relative_to(ROOT)),'l_'+lang+':',bom=True)
manifest=dict(focuses=FOCUSES,decisions=DECISIONS,events=EVENTS,ideas=IDEAS,traits=TRAITS,commanders=COMMANDERS,advisors=ADVISORS,mios=MIO_DATA,army=ARMY_DATA,idea_extra=IDEA_EXTRA,state_sets=STATE_SETS,game_source=str(GAME),target_version='1.18.*',source_version=json.loads(read('launcher-settings.json')).get('version','unknown'))
write('docs/content_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
write('descriptor.mod','version="0.2.0"\ntags={ "Alternative History" "National Focuses" "Events" }\nname="Roma Invicta: Byzantine Restoration"\nsupported_version="1.18.*"')
write('roma_restoration.mod','version="0.2.0"\ntags={ "Alternative History" "National Focuses" "Events" }\nname="Roma Invicta: Byzantine Restoration"\nsupported_version="1.18.*"\npath="'+ROOT.as_posix()+'"')
print(f'Built {len(FOCUSES)} imperial focuses, {len(DECISIONS)} decisions, {len(EVENTS)} events, {len(COMMANDERS)} commanders.')



# Only the imperial route replaces the original debt decision category.
categories=read('common/decisions/categories/GRE_decision_categories.txt')
marker='GRE_pay_back_debt_to_the_ifc_category = {'
categories=categories.replace(marker,marker+' visible = { NOT = { has_completed_focus = RR_empire } }',1)
write('common/decisions/categories/GRE_decision_categories.txt',categories)
