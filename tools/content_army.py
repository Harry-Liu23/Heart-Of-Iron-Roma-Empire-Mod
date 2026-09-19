"""Two independent army branches; executed after existing content corrections."""
IDEA_EXTRA = {}
ARMY_DATA = {
    'entry': 'RR_empire', 'days': 259,
    'infantry': ['RR_new_marian_reforms', 'RR_rebuild_themes', 'RR_state_armories', 'RR_roman_legions'],
    'armor': ['RR_recast_cataphracts', 'RR_revise_strategikon', 'RR_imperial_workshops', 'RR_modern_cataphracts'],
    'final': 'RR_roman_military_glory',
    'theorists': [],
    'training_scope': '部队经验获取与陆军损耗为通用修正，包含演习；不是仅限演习的修正。',
}

# Idea-level research/equipment blocks are separate from scalar country modifiers.
def army_spirit(key, name, mods=None, research=None, equipment=None, desc=None):
    spirit(key, name, mods or {}, desc)
    extra = []
    if research:
        extra.append('research_bonus = { '+' '.join(f'{k} = {v}' for k,v in research.items())+' }')
    if equipment:
        extra.append('equipment_bonus = { '+' '.join(
            k+' = { instant = yes '+' '.join(f'{m} = {v}' for m,v in values.items())+' }'
            for k,values in equipment.items())+' }')
    IDEA_EXTRA[fid(key)] = '\n'.join(extra)

army_spirit('marian_reform_spirit', '新马略军改', {'experience_gain_army': .05},
    research={'infantry_weapons': .05, 'artillery': .05})
army_spirit('military_themes_spirit', '军区训练体系',
    {'training_time_army_factor': -.15, 'experience_gain_army_unit_factor': .20, 'attrition': -.15},
    desc='统一军区征募与训练：部队经验获取+20%，陆军损耗−15%，两项也适用于演习之外。')
army_spirit('cataphract_research_spirit', '铁甲骑兵现代化', research={'armor': .05})
army_spirit('strategikon_spirit', '重修《战略论》',
    {'experience_gain_army_factor': .10, 'land_doctrine_cost_factor': -.10})
army_spirit('state_armories_spirit', '国家军械所', equipment={
    'infantry_equipment': {'build_cost_ic': -.20},
    'artillery_equipment': {'build_cost_ic': -.15},
    'anti_tank_equipment': {'build_cost_ic': -.15},
    'anti_air_equipment': {'build_cost_ic': -.15},
    'rocket_artillery_equipment': {'build_cost_ic': -.15},
    'support_equipment': {'build_cost_ic': -.15},
})
# armor is the equipment type shared by tanks and their chassis/legacy variants.
# Armored cars are motorized equipment, so must be included explicitly.
army_spirit('imperial_workshops_spirit', '帝国御用兵工坊', equipment={
    'armor': {'build_cost_ic': -.15, 'reliability': .05},
    'armored_car_equipment': {'build_cost_ic': -.15, 'reliability': .05},
})
army_spirit('modern_cataphracts_spirit', '现代铁甲圣骑兵', equipment={
    k: {'maximum_speed': .10, 'soft_attack': .15, 'hard_attack': .15, 'defense': .15}
    for k in ['armor', 'armored_car_equipment']
})
army_spirit('roman_military_glory_spirit', '罗马军威再临',
    {'army_org_factor': .05, 'army_org_regain': .10, 'supply_consumption_factor': -.10, 'max_planning_factor': .10})

# Add advisor roles to the existing people, preserving all original commander roles.
for key,title,unlock,mods,research in [
    ('john_ii','军团战争理论家','rebuild_themes',
     {'experience_gain_army': .20, 'land_doctrine_cost_factor': -.10},
     {'infantry_weapons': .05, 'artillery': .05}),
    ('heraclius','装甲战争理论家','revise_strategikon',
     {'experience_gain_army': .20, 'land_doctrine_cost_factor': -.10}, {'armor': .10}),
    ('alexios_i','帝国战争理论家','roman_military_glory',
     {'experience_gain_army': .25, 'land_doctrine_cost_factor': -.15, 'experience_gain_army_factor': .10}, {}),
]:
    trait='RR_'+key+'_theorist_trait'
    token='RR_'+key+'_theorist'
    TRAITS[trait]=mods
    loc(trait,title)
    person=next(c for c in COMMANDERS if c[0]==key)
    loc(token,person[1])
    loc(token+'_desc',title+'；任命到军官团理论家席位后生效。')
    loc('RR_unlock_'+key+'_theorist_tt','开放'+person[1]+'担任'+title+'（理论家席位，100政治点）。')
    role='''advisor = { slot = theorist idea_token = %s ledger = army
        allowed = { original_tag = GRE } available = { has_completed_focus = %s }
        traits = { %s } cost = 100
        research_bonus = { %s }
    }''' % (token, fid(unlock),trait,' '.join(f'{k} = {v}' for k,v in research.items()))
    index=next(i for i,s in enumerate(CHARACTERS) if s.startswith('RR_'+key+' ='))
    s=CHARACTERS[index]; pos=s.rfind('}')
    CHARACTERS[index]=s[:pos]+role+'\n'+s[pos:]
    ARMY_DATA['theorists'].append(dict(character='RR_'+key,token=token,trait=trait,
        title=title,unlock=fid(unlock),research=research,cost=100))
write('common/characters/rr_court.txt','characters = {\n'+'\n'.join(CHARACTERS)+'\n}')

# Replace only Belisarius' army-chief role. Preserve active status without displacing
# a different chief, and preserve his commander identity and all its traits.
TRAITS['RR_marian_reformer_trait'] = {'army_attack_factor': .10, 'experience_gain_army': .15, 'training_time_army_factor': -.10}
loc('RR_marian_reformer_trait','新马略军改倡导者')
loc('RR_belisarius_reformed','贝利萨留')
loc('RR_marian_minister_tt','贝利萨留升级为新马略军改倡导者：陆军攻击+10%、每日陆军经验+0.15、训练时间−10%；任命费用75政治点。已任命则保留在任。')
new_chief='''add_advisor_role = { character = RR_belisarius
    advisor = { slot = army_chief idea_token = RR_belisarius_reformed ledger = army
        allowed = { original_tag = GRE } available = { has_completed_focus = RR_new_marian_reforms }
        traits = { RR_marian_reformer_trait } cost = 75 }
    ACTIVATE
}'''
EFFECTS['RR_upgrade_marian_minister']='''if = { limit = { has_idea = RR_belisarius }
    remove_advisor_role = { character = RR_belisarius slot = army_chief }
    %s
} else = {
    remove_advisor_role = { character = RR_belisarius slot = army_chief }
    %s
}''' % (new_chief.replace('ACTIVATE','activate = yes'),new_chief.replace('ACTIVATE',''))

# Extend the existing initial MIO traits, never add an unlockable military trait.
path='common/military_industrial_organization/organizations/rr_organizations.txt'
s=(ROOT/path).read_text(encoding='utf-8')
initial_names={'piraeus':'军团军械标准','ankara_armor':'帝国装甲标准','thessaloniki':'军区运输体系'}
updated=[]
for key,name,state,equipment,categories,eqbonus,production in MIO_DATA:
    if key in initial_names:
        old=get_block(s,'RR_mio_'+key)
        new=old.replace('equipment_bonus = { '+eqbonus+' }',
            'equipment_bonus = { '+eqbonus+' build_cost_ic = -.05'+(' reliability = .05' if key=='thessaloniki' else '')+' }',1)
        eqbonus+=' build_cost_ic = -.05'+(' reliability = .05' if key=='thessaloniki' else '')
        if key=='ankara_armor':
            new=new.replace('equipment_type = { armor }','equipment_type = { armor armored_car_equipment }')
            equipment='armor armored_car_equipment'
        assert new!=old, 'MIO initial trait patch failed: '+key
        s=s.replace(old,new,1)
        loc('RR_mio_'+key+'_initial',initial_names[key])
    updated.append((key,name,state,equipment,categories,eqbonus,production))
MIO_DATA[:]=updated
write(path,s)

# Award only after existing enterprise initialization. Daily refresh retries missing
# headquarters/unopened enterprises; per-award flags make payouts idempotent.
army_mio_rewards=[]
for focus_key,company,amount,research in [
    ('state_armories','piraeus',1000,.10),
    ('imperial_workshops','ankara_armor',1000,.10),
    ('roman_military_glory','piraeus',500,0),
    ('roman_military_glory','ankara_armor',500,0),
    ('roman_military_glory','thessaloniki',500,0),
]:
    token='RR_mio_'+company
    state=next(row[2] for row in MIO_DATA if row[0]==company)
    paid='RR_army_paid_'+focus_key+'_'+company
    ready='RR_army_reward_'+focus_key
    army_mio_rewards.append('''if = { limit = {
        has_dlc = "Arms Against Tyranny" has_country_flag = RR_enterprises
        has_country_flag = %s has_country_flag = %s_initialized
        controls_state = %s NOT = { has_country_flag = %s }
    }
        mio:%s = { add_mio_funds = %s %s }
        set_country_flag = %s
    }''' % (ready,token,state,paid,token,amount,
        'add_mio_research_bonus = .10' if research else '',paid))
EFFECTS['RR_settle_army_mio_rewards']='\n'.join(army_mio_rewards)
EFFECTS['RR_update_enterprises']+='\nRR_settle_army_mio_rewards = yes'
loc('RR_army_mio_pending_tt','军工机构奖励只兑现一次；企业尚未开放或未控制所在地时保留，企业开放并控制所在地后自动兑现。需要Arms Against Tyranny。')

# Completion flags are set explicitly: has_completed_focus need not be true while
# its own completion_reward is executing.
def army_mio_reward(key):
    return 'set_country_flag = RR_army_reward_'+key+' RR_update_enterprises = yes'

def army_research(category,uses,name):
    return 'add_tech_bonus = { name = '+name+' bonus = .5 uses = '+str(uses)+' category = '+category+' }'

focus('new_marian_reforms','新马略军改','陆军：步兵',(117,3),['empire'],21,
    'add_army_experience = 25 '+idea('marian_reform_spirit')+' '+
    army_research('infantry_weapons',1,'RR_new_marian_reforms')+' '+
    army_research('artillery',1,'RR_new_marian_reforms')+
    ' custom_effect_tooltip = RR_marian_minister_tt hidden_effect = { RR_upgrade_marian_minister = yes }',
    '陆军经验+25、每日陆军经验+0.05；步兵装备和火炮各1次50%研究加成，两类研究速度永久+5%；贝利萨留升级为75政治点的改革版陆军部长。')
focus('rebuild_themes','重建军区制','陆军：步兵',(117,4),['new_marian_reforms'],28,
    idea('military_themes_spirit')+' custom_effect_tooltip = RR_unlock_john_ii_theorist_tt',
    '训练时间−15%、部队经验获取+20%、陆军损耗−15%（包含演习）；开放约翰二世为军团战争理论家。',
    available='num_divisions > 7')
focus('state_armories','重建国家军械所','陆军：步兵',(117,5),['rebuild_themes'],28,
    idea('state_armories_spirit')+' '+army_mio_reward('state_armories')+' custom_effect_tooltip = RR_army_mio_pending_tt',
    '步兵装备成本−20%；牵引火炮、防空炮、反坦克炮、火箭炮及支援装备成本−15%；比雷埃夫斯兵工局经费+1000、机构研究加成+10个百分点，未开放时保留。',
    available='num_of_military_factories > 2')
focus('roman_legions','罗马军团','陆军：步兵',(117,6),['state_armories'],35,
    '''add_unit_bonus = {
        infantry = { max_organisation = 10 defense = .15 soft_attack = .10 name = RR_roman_legions }
        artillery = { soft_attack = .10 name = RR_roman_legions }
        artillery_brigade = { soft_attack = .10 name = RR_roman_legions }
    }''',
    '普通徒步步兵组织度+10、防御+15%、软攻击+10%；牵引火炮（含支援炮兵）软攻击+10%。永久国策加成，不解锁专属科技。')
focus('recast_cataphracts','重铸铁甲骑兵','陆军：装甲',(121,3),['empire'],21,
    'add_army_experience = 25 '+idea('cataphract_research_spirit')+' '+army_research('armor',2,'RR_recast_cataphracts'),
    '陆军经验+25；2次坦克科技50%研究加成；坦克科技研究速度永久+5%。')
focus('revise_strategikon','重修《战略论》','陆军：装甲',(121,4),['recast_cataphracts'],28,
    'add_army_experience = 30 '+idea('strategikon_spirit')+' custom_effect_tooltip = RR_unlock_heraclius_theorist_tt',
    '陆军经验+30、陆军经验获取+10%、陆军学说花费−10%；开放希拉克略为装甲战争理论家。')
focus('imperial_workshops','帝国御用兵工坊','陆军：装甲',(121,5),['revise_strategikon'],28,
    idea('imperial_workshops_spirit')+' '+army_mio_reward('imperial_workshops')+' custom_effect_tooltip = RR_army_mio_pending_tt',
    '坦克及衍生车辆、装甲车生产成本−15%、可靠性+5个百分点；安纳托利亚装甲联合厂经费+1000、机构研究加成+10个百分点，未开放时保留。',
    available='num_of_military_factories > 2')
focus('modern_cataphracts','现代铁甲圣骑兵','陆军：装甲',(121,6),['imperial_workshops'],35,
    idea('modern_cataphracts_spirit'),
    '坦克、坦克歼击车、自行火炮、自行防空炮及装甲车移动速度+10%、软硬攻击+15%、防御+15%；不增加突破，不解锁专属科技。')
focus('roman_military_glory','罗马军威再临','陆军：合流',(119,7),['roman_legions','modern_cataphracts'],35,
    '''add_army_experience = 75 add_political_power = 100
    capital_scope = { add_extra_state_shared_building_slots = 2
        add_building_construction = { type = arms_factory level = 2 instant_build = yes } }
    '''+idea('roman_military_glory_spirit')+' '+army_mio_reward('roman_military_glory')+
    ' custom_effect_tooltip = RR_army_mio_pending_tt custom_effect_tooltip = RR_unlock_alexios_i_theorist_tt',
    '两线完成后：陆军经验+75、政治点+100、首都2军工及2建筑槽；陆军组织度+5%、恢复+10%、补给消耗−10%、计划上限+10%；三家陆军企业各500经费；开放阿莱克修斯一世为帝国战争理论家。')