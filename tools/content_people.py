
# Characters, advisors and territory-bound industrial organizations.
CHARACTERS, TRAITS, CONCERNS, MIOS = [], {}, [], []
COMMANDERS = [
 ('belisarius','贝利萨留',4,'brilliant_strategist war_hero career_officer trickster',False),
 ('heraclius','希拉克略',4,'brilliant_strategist panzer_leader career_officer trait_cautious',False),
 ('john_ii','约翰二世·科穆宁',3,'brilliant_strategist trait_mountaineer trait_cautious',False),
 ('ouranos','尼基弗鲁斯·乌拉诺斯',3,'career_officer infantry_leader trickster',False),
 ('troglita','约翰·特罗格利塔',3,'cavalry_leader war_hero trait_cautious',False),
 ('axouch','约翰·阿克苏赫',3,'career_officer organizer trait_cautious',False),
 ('philanthropenos','阿莱克修斯·菲兰斯罗佩诺斯',3,'trickster trait_reckless war_hero',False),
 ('kekaumenos','卡塔卡隆·凯考梅诺斯',3,'trait_mountaineer career_officer trait_reckless',False),
 ('argyros','尤斯塔修斯·阿尔吉罗斯',2,'cavalry_leader old_guard trait_cautious',False),
 ('lachanodrakon','米海尔·拉哈诺德拉孔',2,'infantry_leader harsh_leader old_guard',False),
 ('leo_iii','利奥三世',3,'inflexible_strategist war_hero career_officer',False),
 ('constantine_v','君士坦丁五世',3,'infantry_leader career_officer trait_reckless',False),
 ('alexios_i','阿莱克修斯一世·科穆宁',3,'brilliant_strategist organizer logistics_wizard trait_cautious',True),
 ('kourkouas','约翰·库尔库阿斯',4,'inflexible_strategist unyielding_defender defensive_doctrine old_guard',True)]
TRAITS['RR_purple_emperor']={'stability_factor':.05,'war_support_factor':.05}
TRAITS['RR_imperial_administrator']={'political_power_gain':.15}
loc('RR_purple_emperor','紫衣归来');loc('RR_imperial_administrator','帝国行政之首')
loc('RR_constantine','君士坦丁十一世')
CHARACTERS.append('''RR_constantine = {
 name = RR_constantine
 portraits = { civilian = { large = "gfx/leaders/Europe/portrait_europe_generic_1.dds" } }
 country_leader = { ideology = roman_restoration traits = { RR_purple_emperor } expire = "1970.1.1" }
}''')
for i,(key,name,level,traits,marshal) in enumerate(COMMANDERS):
    loc('RR_'+key,name)
    # Generic art is explicit placeholder art, not a claim to depict the historical person.
    portrait='gfx/leaders/Europe/Portrait_Europe_Generic_land_1.dds'
    role='field_marshal' if marshal else 'corps_commander'
    skill=[(3,3,4,3),(3,3,4,3),(2,3,3,2)][min(2,4-level)]
    advisor=''
    if key in ['belisarius','heraclius']:
        slot='army_chief' if key=='belisarius' else 'high_command'
        trait='army_chief_offensive_2' if key=='belisarius' else 'army_armored_1'
        advisor=f'''advisor = {{ slot = {slot} idea_token = RR_{key} ledger = army
          allowed = {{ original_tag = GRE }} available = {{ has_completed_focus = RR_empire }}
          traits = {{ {trait} }} cost = 150 }}'''
    CHARACTERS.append(f'''RR_{key} = {{ name = RR_{key}
      portraits = {{ army = {{ large = "{portrait}" small = GFX_idea_generic_army_chief }} }}
      {role} = {{ traits = {{ {traits} }} skill = {level}
      attack_skill = {skill[0]} defense_skill = {skill[1]} planning_skill = {skill[2]} logistics_skill = {skill[3]} }}
      {advisor}
    }}''')

ADVISORS=[
 ('narses','纳尔西斯',125,'empire',{'political_power_gain':.15,'industrial_capacity_factory':.03,'intel_network_gain_factor':.1}),
 ('propagandist','帝国宣传官',75,'empire',{'empire_drift':.08,'stability_factor':.03,'research_speed_factor':.02}),
 ('reconstruction_minister','重建大臣',100,'empire',{'production_speed_industrial_complex_factor':.05,'production_speed_infrastructure_factor':.1,'decryption_factor':.05}),
 ('palace_intelligence','宫廷情报总监',100,'empire',{'intel_network_gain_factor':.05,'empire_drift':.03,'political_power_gain':.05,'counter_intelligence':.5}),
 ('military_secretary','军务大臣',125,'empire',{'experience_gain_army':.03,'training_time_army_factor':-.05,'political_power_gain':.05}),
 ('frontier_governor','边疆总督',100,'government',{'conscription_factor':.05,'army_core_defence_factor':.03,'resistance_growth':-.05}),
 ('cipher_director','帝国密码局长',125,'government',{'decryption_factor':.1,'agency_upgrade_time':-.1}),
 ('overseas_director','海外事务总监',125,'government',{'intel_network_gain_factor':.15,'operation_cost':-.1}),
 ('senate_secretary','元老院秘书',100,'flag:senate_rebuilt',{'political_power_gain':.2,'stability_factor':.03}),
 ('jurist','大法官',100,'codex',{'laws_cost':-.15,'political_advisor_cost_factor':-.15,'drift_defence_factor':.25}),
 ('census_minister','人口事务大臣',100,'flag:census_done',{'conscription_factor':.1,'mobilization_speed':.1}),
 ('university_director','大学总监',100,'scholars',{'research_speed_factor':.05,'special_project_speed_factor':.05})]
for key,name,cost,unlock,mods in ADVISORS:
    loc('RR_'+key,name);loc('RR_'+key+'_trait',name)
    TRAITS['RR_'+key+'_trait']=mods
    available=flag(unlock[5:]) if unlock.startswith('flag:') else done(unlock)
    CHARACTERS.append(f'''RR_{key} = {{ name = RR_{key}
      portraits = {{ civilian = {{ large = "gfx/leaders/Europe/portrait_europe_generic_1.dds" small = GFX_idea_generic_political_advisor }} }}
      advisor = {{ slot = political_advisor idea_token = RR_{key} allowed = {{ original_tag = GRE }}
      available = {{ {available} }} traits = {{ RR_{key}_trait }} cost = {cost} }}
    }}''')
EFFECTS['RR_recruit_court']='\n'.join('recruit_character = RR_'+k for k in ['constantine']+[x[0] for x in COMMANDERS]+[x[0] for x in ADVISORS])
write('common/characters/rr_court.txt','characters = {\n'+'\n'.join(CHARACTERS)+'\n}')
write('common/country_leader/rr_traits.txt','leader_traits = {\n'+'\n'.join(k+' = { '+' '.join(f'{m} = {v}' for m,v in mods.items())+' }' for k,mods in TRAITS.items())+'\n}')

# Civilian companies have tiered industrial-concern ideas, not fake MIO levels.
for key,name,mods1,mods2 in [
 ('construction','雅典帝国建设总公司',{'production_speed_industrial_complex_factor':.05,'production_speed_infrastructure_factor':.1},{'production_speed_industrial_complex_factor':.1,'production_speed_infrastructure_factor':.15}),
 ('electrical','帝国机械与电气公司',{'industry_research':.05,'electronics_research':.05},{'industry_research':.075,'electronics_research':.075})]:
    for tier,mods in [(1,mods1),(2,mods2)]:
        token=f'RR_{key}_{tier}'
        loc(token,name+('Ⅰ' if tier==1 else 'Ⅱ'));loc(token+'_desc','控制雅典时可任用；失去所在地停用。')
        condition='NOT = { has_completed_focus = RR_industrial_combine }' if tier==1 else done('industrial_combine')
        CONCERNS.append(f'''{token} = {{
          picture = generic_industrial_concern_1 allowed = {{ original_tag = GRE }}
          available = {{ has_country_flag = RR_enterprises controls_state = 47 {condition} }}
          visible = {{ has_country_flag = RR_enterprises {condition} }}
          cost = 100 modifier = {{ {' '.join(f'{m} = {v}' for m,v in mods.items())} }}
        }}''')
EFFECTS['RR_upgrade_concerns']='\n'.join(f'if = {{ limit = {{ has_idea = RR_{k}_1 }} swap_ideas = {{ remove_idea = RR_{k}_1 add_idea = RR_{k}_2 }} }}' for k in ['construction','electrical'])
write('common/ideas/rr_concerns.txt','ideas = { industrial_concern = {\n'+'\n'.join(CONCERNS)+'\n} }')

MIO_DATA=[
 ('piraeus','比雷埃夫斯兵工局',47,'infantry_equipment artillery_equipment','infantry_weapons artillery','reliability = .05',''),
 ('thessaloniki','塞萨洛尼基车辆工厂',731,'motorized_equipment mechanized_equipment','motorized_equipment','', 'production_efficiency_gain_factor = .05'),
 ('naval_office','帝国海军船政局',47,'capital_ship screen_ship','naval_equipment','reliability = .05',''),
 ('constantinople_shipyard','君士坦丁堡帝国造船厂',797,'capital_ship','naval_equipment','reliability = .05',''),
 ('smyrna_aircraft','士麦那航空工厂',339,'small_plane_airframe','light_air','range = .05',''),
 ('ankara_armor','安纳托利亚装甲联合厂',49,'armor','armor','reliability = .05','')]
updates=[]
for key,name,state,equipment,categories,eqbonus,production in MIO_DATA:
    token='RR_mio_'+key
    loc(token,name);loc(token+'_initial','帝国生产章程');loc(token+'_quality','质量检验');loc(token+'_workshops','扩建车间');loc(token+'_funds','国家兵工拨款')
    MIOS.append(f'''{token} = {{
      name = {token} icon = GFX_idea_generic_industrial_concern
      allowed = {{ original_tag = GRE has_dlc = "Arms Against Tyranny" }}
      visible = {{ owner = {{ has_country_flag = RR_enterprises }} }}
      available = {{ owner = {{ has_country_flag = RR_enterprises controls_state = {state} }} }}
      equipment_type = {{ {equipment} }} research_categories = {{ {categories} }}
      research_bonus = 0
      initial_trait = {{ name = {token}_initial equipment_bonus = {{ {eqbonus} }}
        production_bonus = {{ production_capacity_factor = .05 {production} }} }}
      trait = {{ token = RR_quality name = {token}_quality position = {{ x = 0 y = 0 }}
        equipment_bonus = {{ reliability = .02 }} }}
      trait = {{ token = RR_workshops name = {token}_workshops position = {{ x = 1 y = 1 }}
        any_parent = {{ RR_quality }} production_bonus = {{ production_capacity_factor = .02 }} }}
    }}''')
    updates.append(f'''if = {{ limit = {{ has_dlc = "Arms Against Tyranny" has_country_flag = RR_enterprises controls_state = {state} NOT = {{ has_country_flag = {token}_initialized }} }}
      mio:{token} = {{ add_mio_size = 1 }}
      set_country_flag = {token}_initialized
    }}''')
    if key=='piraeus':
        # A reusable modifier is added once, and removed while the headquarters is lost.
        EFFECTS['RR_arsenal_funds']=f'''if = {{ limit = {{ has_dlc = "Arms Against Tyranny" }} mio:{token} = {{ add_mio_modifier = {{ modifier = RR_arsenal_funding }} }} }}'''
updates.append('''if = { limit = { NOT = { controls_state = 47 } }
  if = { limit = { has_idea = RR_construction_1 } set_country_flag = RR_restore_construction remove_ideas = RR_construction_1 }
  if = { limit = { has_idea = RR_construction_2 } set_country_flag = RR_restore_construction remove_ideas = RR_construction_2 }
  if = { limit = { has_idea = RR_electrical_1 } set_country_flag = RR_restore_electrical remove_ideas = RR_electrical_1 }
  if = { limit = { has_idea = RR_electrical_2 } set_country_flag = RR_restore_electrical remove_ideas = RR_electrical_2 }
}''')
for k in ['construction','electrical']:
    updates.append(f'''if = {{ limit = {{ controls_state = 47 has_country_flag = RR_restore_{k} }}
      if = {{ limit = {{ has_completed_focus = RR_industrial_combine }} add_ideas = RR_{k}_2 }} else = {{ add_ideas = RR_{k}_1 }}
      clr_country_flag = RR_restore_{k}
    }}''')
EFFECTS['RR_update_enterprises']='\n'.join(updates)
write('common/military_industrial_organization/organizations/rr_organizations.txt','\n'.join(MIOS))
# MIO modifiers use the same modifier-definition directory as vanilla MIOs.
write('common/military_industrial_organization/modifiers/rr_modifiers.txt','RR_arsenal_funding = { military_industrial_organization_funds_gain = .1 }')
loc('RR_arsenal_funding','国家兵工拨款')


