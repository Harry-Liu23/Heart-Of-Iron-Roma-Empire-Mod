
# Late content corrections, applied before emission so source and manifest agree.
# A missing Balkan country is skipped; only countries present at the demand need integrating.
rights=next(f for f in FOCUSES if f['id']=='RR_balkan_rights')
rights['reward']='\n'.join(f'if = {{ limit = {{ {t} = {{ exists = yes }} }} set_country_flag = RR_balkan_target_{t} }} '+wargoal(t) for t in ['BUL','ALB','YUG','ROM'])
province=next(f for f in FOCUSES if f['id']=='RR_balkan_provinces')
province['available']='\n'.join('OR = { NOT = { has_country_flag = RR_balkan_target_'+t+' } AND = { '+own(STATE_SETS[t])+' } }' for t in ['BUL','ALB','YUG','ROM'])
province['reward']='\n'.join(f'{s} = {{ if = {{ limit = {{ is_owned_by = ROOT is_controlled_by = ROOT }} add_core_of = ROOT }} }}' for s in BALKANS)+buildings(47,'industrial_complex',2,2)
province['summary']='整合已收复的巴尔干地区为核心；本土2民工、2槽。只要求统一提出要求时仍存在的目标国家；已不存在的国家跳过。'
# Accepted Italian terms have a concrete territorial outcome and cannot strand the branch.
e=next(e for e in EVENTS if e['id']=='rr.20')
e['body']='拜占庭提出西部帝冠协定：意大利交接本土地区，保留海外属地。接受意味着终止半岛上的主权争端；拒绝将使历史争论转化为军事对抗。'
e['options'][1]=('接受协定，交接意大利本土。','\n'.join(f'if = {{ limit = {{ owns_state = {s} }} GRE = {{ transfer_state = {s} }} }}' for s in ITALY),10)
loc('rr.20.d',e['body']);loc('rr.20.1',e['options'][1][0])
# Late capital decisions must not reverse the already chosen Roman capital or stack tiers.
next(d for d in DECISIONS if d['id']=='RR_capital_constantinople')['visible']+=' NOT = { has_country_flag = RR_rome_proclaimed }'
# Permanent education survives a change of government.
# Generic asset names are mapped to actual bundled assets.
CHARACTERS[:]=[s.replace('GFX_idea_generic_army_chief','GFX_idea_generic_army_chief_off_western_european_2d').replace('GFX_idea_generic_political_advisor ','GFX_idea_generic_political_advisor_europe_1 ') for s in CHARACTERS]
write('common/characters/rr_court.txt','characters = {\n'+'\n'.join(CHARACTERS)+'\n}')
MIO_DATA[:]=[(k,n,s,('mio_cat_eq_all_small_plane' if k=='smyrna_aircraft' else eq),cats,eb,pb) for k,n,s,eq,cats,eb,pb in MIO_DATA]
p=ROOT/'common/military_industrial_organization/organizations/rr_organizations.txt'
write(str(p.relative_to(ROOT)),p.read_text(encoding='utf-8').replace('GFX_idea_generic_industrial_concern','GFX_idea_generic_industrial_concern_1').replace('equipment_type = { small_plane_airframe }','equipment_type = { mio_cat_eq_all_small_plane }'))
# Use original cosmetic flags in each size. No invented portrait or flag artwork.
for target,source in [('RR_BYZ','BYZ_UNIFIED_neutrality'),('RR_ROM','SPQR_UNIFIED_neutrality'),('GRE_empire','BYZ_UNIFIED_neutrality')]:
    for size in ['', 'medium', 'small']:
        src=GAME/'gfx/flags'/size/(source+'.tga')
        for suffix in (['','_empire'] if target!='GRE_empire' else ['']):
            dst=ROOT/'gfx/flags'/size/(target+suffix+'.tga')
            if src.exists():
                dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
write('interface/rr_ideology.gfx','''spriteTypes = {
 spriteType = { name = "GFX_ideology_empire_group" texturefile = "gfx/interface/ideologies/neutrality_group.dds" }
 spriteType = { name = "GFX_ideology_roman_restoration" texturefile = "gfx/interface/ideologies/neutrality_group.dds" }
}''')
loc('empire_drift','每日帝国支持率')
loc('empire_acceptance','帝国外交接受度')
# No unknown idea token when retiring the Metaxas administration.
EFFECTS['RR_take_power']=EFFECTS['RR_take_power'].replace(' remove_ideas = GRE_metaxism_3','')
# Explicit bypasses for already fulfilled administrative goals, not free extra payouts.
for key in ['RR_referendum','RR_march']:
    next(f for f in FOCUSES if f['id']==key)['bypass']='has_government = empire has_country_leader = { character = RR_constantine ruling_only = yes }'


# Do not overwrite another company hired while the headquarters was lost.
for k in ['construction','electrical']:
    old='if = { limit = { controls_state = 47 has_country_flag = RR_restore_'+k+' }'
    new=old+'\n if = { limit = { amount_taken_ideas = { amount < 1 slots = { industrial_concern } } }'
    EFFECTS['RR_update_enterprises']=EFFECTS['RR_update_enterprises'].replace(old,new)
    EFFECTS['RR_update_enterprises']=EFFECTS['RR_update_enterprises'].replace('clr_country_flag = RR_restore_'+k,'} clr_country_flag = RR_restore_'+k)
