
# Executed by build_mod.py with its shared content helpers.
ECON_MAP = {
 'GRE_force_the_farmers_into_factories':'RR_farmers','GRE_paying_back_our_debts_in_bulk':'RR_bulk_debt',
 'GRE_fiscal_responsibility':'RR_fiscal','GRE_greek_autarky':'RR_autarky',
 'GRE_expand_our_tobacco_industry':'RR_tobacco','GRE_increase_our_mining_operations':'RR_mining',
 'GRE_encourage_tourism':'RR_tourism','GRE_mobilise_our_economy':'RR_mobilize_economy',
 'GRE_rejuvenating_athens':'RR_athens','GRE_making_use_of_our_islands':'RR_islands',
 'GRE_clear_the_slums':'RR_slums','GRE_crack_down_on_foreign_monopolies':'RR_monopolies',
 'GRE_lignite_liquefaction':'RR_lignite','GRE_extracting_more_from_our_soil':'RR_soil',
 'GRE_the_macedonian_farmlands':'RR_farmlands'}
def vanilla_reward(old):
    s = get_block(VANILLA[old], 'completion_reward')
    for a,b in ECON_MAP.items(): s = s.replace(a,b)
    return s

focus('farmers','强制农民进厂','经济：入口',(91,3),['empire'],reward=vanilla_reward('GRE_force_the_farmers_into_factories')+' '+setflag('debt_open'),summary='农业社会转为工业化社会：工厂产出+5%、适役人口系数−7%；一次性稳定度−15；开放原版还债决议。')
focus('bulk_debt','大量偿还债务','经济：入口',(91,4),['farmers'],reward=vanilla_reward('GRE_paying_back_our_debts_in_bulk'),summary='稳定度+5；开放每次50政治点、30天的大额偿债决议。',bypass='OR = { has_country_flag = GRE_completely_debt_free has_country_flag = GRE_defaulted_on_debt_flag }')
focus('fiscal','实现财政独立','企业',(89,5),['bulk_debt'],reward='add_political_power = 120 '+setflag('enterprises')+' RR_update_enterprises = yes',summary='政治点+120；开放帝国工业企业和1级军工机构。要求债务已部分或全部偿还。',available='OR = { has_idea = GRE_debt_to_the_ifc_2 has_idea = GRE_debt_to_the_ifc_3 has_country_flag = GRE_completely_debt_free }')
focus('autarky','实现自给自足','经济：产业',(95,5),['bulk_debt'],reward=vanilla_reward('GRE_greek_autarky'),summary='稳定度+10；有限出口；外国垄断消费品系数惩罚从+40%降至+30%。')
focus('enterprise_bureau','帝国企业总局','企业',(89,6),['fiscal'],reward=buildings(47,'industrial_complex',1,1)+' '+idea('enterprise_office'),summary='1民工、1槽；工业企业任用成本−25%。')
focus('arsenals','扩建国家兵工厂','企业',(87,7),['enterprise_bureau'],reward=buildings(47,'arms_factory',2,2)+' RR_arsenal_funds = yes',summary='2军工、2槽；指定帝国兵工机构资金获取+10%。',mutex=['machinery'])
focus('machinery','发展国营机械工业','企业',(91,7),['enterprise_bureau'],reward=buildings(47,'industrial_complex',2,2)+' '+bonus('industry'),summary='2民工、2槽；1次工业技术50%研究加成。',mutex=['arsenals'])
focus('standardization','工业标准化','企业',(89,8),[('arsenals','machinery')],reward=idea('standards')+' '+bonus('production')+' '+bonus('electronics'),summary='生产效率增长+5%；生产、电子技术各1次50%研究加成。')
focus('industrial_combine','帝国工业联合体','企业',(89,9),['standardization'],reward=idea('industrial_union')+' RR_upgrade_concerns = yes',summary='工厂产出+3%、生产效率上限+5%；国有工业企业升级至Ⅱ级。')
for key,name,old,x,parents,summary,mutex in [
 ('tobacco','扩大烟草产业','GRE_expand_our_tobacco_industry',93,['autarky'],'4民工、4槽；外国垄断消费品惩罚降至+20%；保留贸易关系改善。',['mining']),
 ('mining','扩张采矿工业','GRE_increase_our_mining_operations',97,['autarky'],'3军工、3槽；2次开采技术100%研究加成；外国垄断消费品惩罚降至+20%。',['tobacco']),
 ('tourism','鼓励旅游业','GRE_encourage_tourism',93,[('tobacco','mining')],'一次性稳定度+5；和平旅游精神：稳定度+10、政治点获取+15%、消费品系数−15%；垄断惩罚降至+10%。',['mobilize_economy']),
 ('mobilize_economy','经济动员','GRE_mobilise_our_economy',97,[('tobacco','mining')],'战争支持+5；升级部分动员或战争经济，已战时经济则150政治点；垄断惩罚降至+10%。',['tourism']),
 ('athens','振兴雅典','GRE_rejuvenating_athens',92,[('tourism','mobilize_economy')],'雅典2民工、1军工、4建筑槽。',['islands','slums']),
 ('islands','开发群岛领地','GRE_making_use_of_our_islands',95,[('tourism','mobilize_economy')],'基础2民工、1船坞、5槽；控制塞浦路斯再2军工3槽，控制多德卡尼斯再1船坞1槽；原版塞浦路斯整合。',['athens','slums']),
 ('slums','清理贫民窟','GRE_clear_the_slums',98,[('tourism','mobilize_economy')],'5建筑槽、66,750人力。',['athens','islands'])]:
    y=6 if key in ['tobacco','mining'] else 7 if key in ['tourism','mobilize_economy'] else 8
    focus(key,name,'经济：产业',(x,y),parents,reward=vanilla_reward(old),summary=summary,mutex=mutex,available='has_war_support > .2' if key=='mobilize_economy' else '')
focus('monopolies','打击外国垄断企业','经济：产业',(95,9),[('athens','islands','slums')],reward=vanilla_reward('GRE_crack_down_on_foreign_monopolies'),summary='稳定度+5；移除外国垄断；原版三家本土军工机构开放并各增加1级。')
for i,(key,name,old,summary) in enumerate([
 ('lignite','褐煤液化','GRE_lignite_liquefaction','1合成炼油厂、1建筑槽。'),
 ('soil','开拓土地资源','GRE_extracting_more_from_our_soil','指定希腊州铝+41、钢+24、钨+5。'),
 ('farmlands','马其顿富饶沃土','GRE_the_macedonian_farmlands','损耗−5%、补给消耗−5%、核心补给战斗惩罚−10%、补给范围+10%、消费品系数−5%。')]):
    focus(key,name,'经济：资源',(102,3+i),['empire' if i==0 else ['lignite','soil'][i-1]],reward=vanilla_reward(old),summary=summary,available='731 = { is_fully_controlled_by = ROOT is_core_of = ROOT }' if i==2 else '')
focus('scholars','召回流亡学者','科研',(108,6),['government'],reward=bonus('electronics'),summary='1次电子技术50%研究加成；开放大学总监：任用时科研+5%、特别项目研究+5%。')
focus('university','重建帝国大学','科研',(108,7),['scholars'],70,'RR_research_slot = yes RR_set_science1 = yes','新增1科研槽；科研体系+3%；开放教育体系与高教标准决议。')
focus('academy','帝国科学研究院','科研',(108,8),['university'],reward='RR_research_slot = yes RR_set_science3 = yes '+bonus('engineering'),summary='新增1科研槽；科研体系升级至+7%；1次工程类50%研究加成。',available='date > 1937.12.31')
focus('academic_commonwealth','罗马学术共同体','科研',(108,9),['academy'],reward='RR_research_slot = yes RR_set_science4 = yes',summary='新增1科研槽，最终6槽；科研体系最终+10%。',available='date > 1938.12.31')
focus('facility_office','实验设施管理局','实验设施',(112,6),['government'],14,idea('facilities'),'实验设施建设速度+20%。')
focus('research_committee','专项研究委员会','实验设施',(112,7),['facility_office'],14,idea('committee'),'特别项目研究速度+15%；开放100政治点、180天国家实验室计划。')
focus('scientist_training','科学家培养计划','实验设施',(112,8),['research_committee'],14,idea('scientists'),'科学家研究加成+10%、突破贡献+10%。')

decision('rebuild_senate','重建元老院',100,45,done('government'),'',
 setflag('senate_rebuilt'),'100政治点，45天；开放法典国策和元老院秘书。')
decision('population_census','帝国人口普查',125,60,done('government'),'',setflag('census_done')+' '+idea('census')+' if = { limit = { NOT = { OR = { has_idea = extensive_conscription has_idea = service_by_requirement has_idea = all_adults_serve has_idea = scraping_the_barrel } } } add_ideas = extensive_conscription }','125政治点，60天；适役人口系数+10%、动员速度+15%；免费升至广泛征兵，保留更高法律。')
decision('provincial_council','重建行省议会',100,45,done('themes'),'','if = { limit = { NOT = { OR = { has_country_flag = RR_central has_country_flag = RR_pronoia } } } RR_set_provincial2 = yes } '+setflag('council_done'),'100政治点，45天；制度选择前行省每日政治点升至+0.15；不阻挡后续国策，制度选择后不覆盖更高档位。')
decision('institution_meeting','召开帝国制度会议',125,30,done('eastern_empire'),'','country_event = { id = rr.11 }','125政治点，30天；事件二选一：中央集权军区制或新普罗尼亚体系。')
decision('civic_schooling','公民教育改革',100,60,done('private_faith'),'',setflag('civic_education')+' RR_set_identity2 = yes','100政治点，60天；认同精神改为稳定度0、战争支持−5、科研+3%、适役人口系数+5%；开放罗马人的共同体。')
decision('turkey_demand','对土交涉',75,0,done('legitimacy'),'date > 1936.12.31 has_government = empire is_subject = no NOT = { has_war_with = TUR } OR = { is_in_faction = no is_faction_leader = yes } TUR = { exists = yes }','TUR = { country_event = { id = rr.5 } }','75政治点，1937年1月1日起；帝国执政、独立、与土耳其和平、不在外国领导的阵营。土耳其90%拒绝并立即开战，10%接受并割让约定领土。')
decision('capital_constantinople','迁都君士坦丁堡',25,0,done('jewel'),done('new_rome')+' has_war = no '+own([797]),'set_capital = { state = 797 } RR_rename_constantinople = yes '+buildings(797,'industrial_complex',1,2)+buildings(797,'infrastructure',1)+' 797 = { add_dynamic_modifier = { modifier = RR_capital_base } } '+setflag('capital_built'),'25政治点；迁都并更名君士坦丁堡；1民工、2槽、1基础设施；当地建设+10%、防御+5%、适役人口+10%。')
decision('holy_city','圣城守护者',0,0,done('antioch'),own([454]),'add_stability = .05 '+cores([454,455])+' '+setflag('holy_city'),'免费，立即；控制并拥有耶路撒冷后稳定度+5，整合圣地；不影响后续国策。')
decision('granary','帝国的粮仓',100,7,done('great_restoration'),'',regional_goal(EGYPT),'100政治点，7天；获得对埃及目标地区外国拥有者的365天吞并战争目标；不阻挡亚历山大国策。')
decision('our_sea','我们的海',100,30,done('antioch')+' '+done('alexandria'),own(LEVANT+EGYPT),'add_navy_experience = 50 '+idea('mare')+' '+setflag('mare_done'),'100政治点，30天；海军经验+50、船坞产出+5%；满足罗马重建条件。')
decision('proclaim_rome','宣布罗马帝国重建',100,0,done('restore_rome'),own([797,2]),'country_event = { id = rr.13 }','100政治点，一次性；国名改为罗马帝国，选择君士坦丁堡或罗马为首都并建设该城。')
decision('higher_education','统一高等教育标准',75,45,done('university')+' NOT = { '+done('academy')+' }','','if = { limit = { NOT = { OR = { has_idea = RR_science3 has_idea = RR_science4 } } } RR_set_science2 = yes }','75政治点，45天；提前将科研体系升至+5%；已有更高阶段则不覆盖。')
decision('education_system','建立教育体系',125,180,done('university'),'',idea('education')+' '+setflag('education_done')+' country_event = { id = rr.14 }','125政治点，180天；永久科研+3%，每月稳定度+0.1个百分点；不阻挡后续国策。')
decision('national_laboratory','国家实验室计划',100,180,done('research_committee'),'has_dlc = "Gotterdammerung"','country_event = { id = rr.15 }','100政治点，180天；选择建设1座陆战、海军或航空实验设施。不阻挡后续国策，需要特别项目DLC。')
for key,name,cost,duration,cooldown,mods,visible in [
 ('assembly','公民大会',25,90,180,{'empire_drift':.05},done('programme')),
 ('tour','皇帝巡省',35,90,180,{'stability_factor':.05,'political_power_gain':.2},'has_government = empire'),
 ('registration','公民登记动员',50,120,240,{'conscription_factor':.1,'mobilization_speed':.1},done('citizenship')),
 ('conference','帝国学术会议',50,180,365,{'research_speed_factor':.05,'special_project_speed_factor':.05},done('university')),
 ('emergency_research','紧急科研拨款',75,180,365,{'research_speed_factor':.1},done('academy')),
 ('legal_review','法律编纂',50,120,365,{'laws_cost':-.15,'political_advisor_cost_factor':-.15},done('codex')),
 ('festival','罗马庆典',75,180,365,{'stability_factor':.1,'war_support_factor':.05},flag('rome_proclaimed'))]:
    spirit(key,name,mods)
    av=f'NOT = {{ has_idea = RR_{key} }}'
    if key in ['conference','emergency_research']: av += ' NOT = { OR = { has_idea = RR_conference has_idea = RR_emergency_research } }'
    decision(key+'_decision',name,cost,duration,visible,av,'',f'{cost}政治点，持续{duration}天，结束后冷却{cooldown}天；同类不能叠加。',once=False,start=timed(key,duration),cooldown=cooldown)
spirit('triumph','凯旋仪式',{'stability_factor':.05,'war_support_factor':.05})
decision('triumph_decision','凯旋仪式',50,90,'has_government = empire',flag('victory_pending')+' NOT = { has_idea = RR_triumph }','','胜利后50政治点，90天稳定度+5、战争支持+5；每场胜利一次。',once=False,start='clr_country_flag = RR_victory_pending '+timed('triumph',90))


