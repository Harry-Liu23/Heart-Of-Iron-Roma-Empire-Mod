# Corrections based on in-game tooltips; keep this before emission.
node('empire')['parents'] = [['GRE_metaxism_focus']]
node('great_restoration')['available'] = 'owns_state = 797 NOT = { country_exists = TUR }'
node('great_restoration')['summary'] = '政治点+150；完成前置国策后，只需拥有君士坦丁堡且土耳其不存在，开放后续制度、宗教和征服分支。'

# Copy the actual vanilla home-restoration reward, retaining the delayed political event.
node('programme')['reward'] = get_block(VANILLA['GRE_restoring_our_home'], 'completion_reward') + '\ncountry_event = { id = rr.1 days = 35 }'
node('programme')['summary'] = '复制原版重建家园奖励：移除沙赫特计划；英国、法国对我国关系各+15，德国−50，意大利−100。完成后再等35天触发帝国问题事件。'

# Atomic upgrades show changes to the existing spirit, rather than remove/add lists.
for key, old, new in [('citizenship','census','citizens'),('warrior_culture','wisdom','culture')]:
    f=node(key)
    f['reward']=f['reward'].replace('remove_ideas = RR_'+old+' add_ideas = RR_'+new,
        'swap_ideas = { remove_idea = RR_'+old+' add_idea = RR_'+new+' }')
# Preserve spirit names across successive upgrades.
for family in [['census','citizens'],['wisdom','culture'],['provincial1','provincial2','central','central_final','pronoia','pronoia_final']]:
    name={'census':'帝国公民制度','wisdom':'帝国文化','provincial1':'帝国行省制度'}[family[0]]
    for key in family:loc('RR_'+key,name)

# Removal effects must only mention spirits that are actually present.
def conditional_removals(s):
    return re.sub(r'(?<!\w)remove_ideas\s*=\s*(\w+)',
        lambda m:'if = { limit = { has_idea = '+m[1]+' } remove_ideas = '+m[1]+' }',s)
for key in ['RR_take_power','RR_end_instability']:
    EFFECTS[key]=conditional_removals(EFFECTS[key])

# Translate flags displayed in availability tooltips.
for key,name in {'crown':'帝国问题事件已选择王冠与双头鹰','basileus':'帝国问题事件已选择执政官巴西琉斯','census_done':'帝国人口普查已完成','civic_education':'公民教育改革已完成','central':'制度会议已选择中央集权军区制','pronoia':'制度会议已选择新普罗尼亚体系','mare_done':'我们的海决议已完成'}.items():
    loc('RR_'+key,name)

# Reuse the vanilla decision and its original territorial checks/rewards.
path='common/decisions/formable_nation_decisions.txt'
s=read(path)
body=get_block(s,'byz_restore_byzantium')
new=body.replace('has_completed_focus = GRE_reviving_the_double_headed_eagle',
    'OR = { has_completed_focus = GRE_reviving_the_double_headed_eagle has_completed_focus = RR_new_rome }')
visible=get_block(new,'visible')
new=new.replace(visible,'\n OR = { AND = { has_completed_focus = GRE_horror_and_fear has_government = fascism } has_completed_focus = RR_new_rome }\n NOT = { has_global_flag = form_byzantine_empire_flag }\n',1)
# Vanilla cosmetic routing does not know the new ideology. Keep the imperial name.
reward=get_block(new,'complete_effect')
new=new.replace(reward,reward+'\n if = { limit = { has_government = empire } set_cosmetic_tag = RR_BYZ RR_rename_constantinople = yes }\n',1)
write(path,s.replace(body,new,1))
node('new_rome')['reward']+=' unlock_decision_tooltip = byz_restore_byzantium'
node('new_rome')['summary']+=' 解锁原版重建拜占庭帝国决议，保留原版领土与独立条件及奖励。'

# The existing emitter locks vanilla focuses after entry. Also block imperial entry
# if an incompatible vanilla branch has already been completed.
excluded={'GRE_bring_home_the_exiled_republicans','GRE_metaxism_focus','GRE_reevaluating_the_drachma'}
blocked=[key for key in VANILLA if key not in excluded]
node('empire')['available']='NOT = { OR = { '+' '.join('has_completed_focus = '+key for key in blocked)+' } }'
# Show explicit reciprocal exclusions for research and political branch roots.
VANILLA_MUTEX=['GRE_compromise_with_the_monarchists','GRE_the_kings_government','GRE_four_year_plan','GRE_request_communist_support']
VANILLA_MUTEX += [key for key in VANILLA if 'research' in key or 'university' in key]
VANILLA_MUTEX=list(dict.fromkeys(key for key in VANILLA_MUTEX if key in VANILLA))
for key in VANILLA_MUTEX:
    if key not in node('empire')['mutex']:node('empire')['mutex'].append(key)
# Keep the entry requirement readable instead of listing the entire vanilla tree.
loc('RR_vanilla_route_clear_tt','尚未进入与帝国路线冲突的原版分支（政治、经济或科研）')
node('empire')['available']='custom_trigger_tooltip = { tooltip = RR_vanilla_route_clear_tt '+node('empire')['available']+' }'
node('programme')['summary']='复制原版重建家园奖励：移除沙赫特计划；民主英国、民主法国对我国关系各+15，德国−50；意大利债务变量≥2.5时，执行原版对意大利债务违约及关系−100。完成后再等35天触发帝国问题事件。'
node('programme')['reward']=conditional_removals(node('programme')['reward'])


node('empire')['mutex']=[x for x in node('empire')['mutex'] if x!='GRE_reevaluating_the_drachma']
node('empire')['reward']+=' add_popularity = { ideology = empire popularity = 0.10 }'
node('empire')['summary']+=' 帝国意识形态基础支持率立即增加10个百分点。'
for key in ['farmers','lignite']:
    node(key)['parents']=[['RR_empire'],['GRE_reevaluating_the_drachma']]
node('fiscal')['available']='OR = { has_idea = GRE_debt_to_the_ifc_2 has_idea = GRE_debt_to_the_ifc_3 has_country_flag = GRE_completely_debt_free has_country_flag = GRE_defaulted_on_debt_flag }'
d=next(d for d in DECISIONS if d['id']=='RR_turkey_demand')
d['available']=d['available'].replace('date > 1936.12.31 ','')
d['summary']=d['summary'].replace('1937年1月1日起；','')
# Decision prose is independent of mechanical reference summaries.
DECISION_PROSE={
'rebuild_senate':'皇帝需要一个能够汇集各方意见的议事机关。重新召集元老，厘清席位与议程，让帝国的法令有一个可以公开辩论的起点。',
'population_census':'从雅典的街巷到乡村的田地，许多居民仍不曾进入完整的国家名册。我们将登记家庭、职业与服役义务，让公民真正成为帝国治理的基础。',
'provincial_council':'首都不可能了解每一座城镇的需要。行省代表将带着地方的账册和诉求前来议事，把中央的法令与地方的实际联系起来。',
'institution_meeting':'军区长官与土地持有者对帝国的未来各有主张。召集制度会议，由皇帝裁定税收、土地与服役义务应当如何安排。',
'civic_schooling':'共同的国家不应只存在于教堂与军营之间。学校将教导年轻人理解公民的权利与责任，让罗马人的身份走入日常生活。',
 'turkey_demand':'双头鹰的法统不能永远停留在演说之中。我们的使节将前往安卡拉，要求土耳其承认拜占庭的正统并交还争议领土。这封照会将决定博斯普鲁斯两岸迎来交接，还是战争。',
'capital_constantinople':'君士坦丁堡再次向我们敞开城门。修缮官署、安置居民，将皇帝与政府迁回海峡之城，让新罗马重新成为帝国的心脏。',
'holy_city':'耶路撒冷的钟声属于许多不同的信众。帝国将承担守护圣地的责任，维持街道与朝圣道路的秩序，让新的统治以安宁证明自身。',
'granary':'尼罗河的收成曾经养育帝国的城市。如今我们必须重新审视南方的航道与粮运，让埃及再次进入帝国的战略视野。',
'our_sea':'从安条克到亚历山大里亚，港口与航道正重新连为一体。协调舰队、码头与海运，使地中海上的帝国据点能够彼此支援。',
'proclaim_rome':'旧罗马与新罗马已经归于同一面旗帜。现在，皇帝与元老院将共同宣布帝国的重建，并决定这份宣言应从哪一座首都传向世界。',
'higher_education':'各大学仍沿用不同的课程与考核办法。由学者共同制定高等教育标准，使知识能够在帝国的院校之间自由传承。',
'education_system':'仅靠几所大学无法支撑国家的未来。我们将培养教师、编订课程并建立教育行政，让城镇与乡村的孩子都能走进课堂。',
'national_laboratory':'研究委员会的图纸已经铺满桌面。集中设备、人才与经费，建设一座能够把理论转化为突破的国家实验设施。',
'assembly_decision':'让公民在广场上听见彼此的声音。公开讨论复兴的目标，将街头的热情凝聚为对帝国事业的支持。',
'tour_decision':'皇帝将离开首都，亲自听取行省的诉求。沿途的接见与巡视应让臣民看见，帝国的关切并不止于宫墙之内。',
'registration_decision':'更新公民名册，并将服役登记带到地方。每一份准确的记录都能减少动员时的混乱，让国家更清楚自己可以依靠谁。',
'conference_decision':'邀请各地学者汇集研究成果。在讲堂与讨论室中交换意见，让孤立的探索成为共同的学术事业。',
'emergency_research_decision':'紧迫的局势不容研究继续等待常规拨款。国库将为重点课题调集资源，让研究人员尽快验证最有希望的方案。',
'legal_review_decision':'旧法令彼此重叠，地方惯例又常与中央规定冲突。法学家将重新整理条文，让官员与公民都能理解法律的边界。',
'festival_decision':'城市将装点街道，广场将迎来庆典。用共同的纪念与欢聚，让帝国的重建成为人民能够亲身参与的时刻。',
'triumph_decision':'归来的军队将穿过首都，接受人民的致意。凯旋仪式既纪念胜利，也铭记那些未能归来的名字。',
'clear_cases':'积压的案件使公民等待，也使地方官署失去信任。派出审理人员清查案卷，让长久悬而未决的争端得到裁断。'
}
for d in DECISIONS:
    d['description']=DECISION_PROSE[d['id'][3:]]
    loc(d['id']+'_desc',d['description'])

# Historical allusions for the two religious policies.
node('faith').update(name='重启圣像之争',summary='政治点+75；圣像崇敬与圣像破坏两条路线互斥。')
rows=[('church_crown','尼西亚的回响',1),('dioceses','修道院与施济所',2),('faith_guard','圣像守护者',3),('sacred_contract','正教的凯旋',4)]
for key,name,i in rows:
    node(key).update(name=name,group='宗教：圣像崇敬')
    loc('RR_church'+str(i),'圣像崇敬：教会与帝国')
    loc('RR_church'+str(i)+'_desc','以圣像崇敬凝聚教区与修道院，通过施济和随军牧养支持帝国。现代政策数值属于架空设计。')
for i,v in [(2,.02),(3,.03),(4,.05)]:IDEAS['RR_church'+str(i)]['army_morale_factor']=v
IDEAS['RR_church3']['research_speed_factor']=-.06
IDEAS['RR_church4'].update(research_speed_factor=-.08,war_support_factor=.15)
for key,summary in [('church_crown','适役人口系数+5%、稳定度+5%、战争支持度+5%、科研速度−3%。'),('dioceses','适役人口系数+15%、稳定度+10%、战争支持度+10%、科研速度−5%、陆军组织度恢复+2%。'),('faith_guard','适役人口系数+25%、稳定度+15%、战争支持度+15%、科研速度−6%、陆军组织度恢复+3%。'),('sacred_contract','适役人口系数+35%、稳定度+20%、战争支持度+15%、科研速度−8%、陆军组织度恢复+5%。')]:
    node(key)['summary']='圣像崇敬精神升级至：'+summary
for key,name,summary in [('private_faith','伊苏里亚敕令','稳定度−5%、战争支持度−10%、每日政治点+0.05；开放整顿教产与学校决议。'),('roman_community','希耶里亚的决议','稳定度+10%、战争支持度+5%、科研速度+5%、适役人口系数+15%、每日政治点+0.10、法律成本−5%。'),('citizen_above_creed','十字架下的皇权','稳定度+15%、战争支持度+10%、科研速度+8%、适役人口系数+25%、每日政治点+0.10、法律成本−5%。')]:
    node(key).update(name=name,group='宗教：圣像破坏',summary='圣像整顿精神升级至：'+summary)
for i in range(1,5):
    loc('RR_identity'+str(i),'圣像整顿：皇权与教会')
    loc('RR_identity'+str(i)+'_desc','以十字架与皇权重订宗教秩序，整顿教产行政并资助学校。教育修正来自现代架空政策，并不代表破坏圣像本身带来科学进步。')
    IDEAS['RR_identity'+str(i)]['political_power_gain']=.05 if i<3 else .10
    if i>=2:IDEAS['RR_identity'+str(i)]['laws_cost']=-.05
IDEAS['RR_identity3']['research_speed_factor']=.05
IDEAS['RR_identity4']['research_speed_factor']=.08
d=next(d for d in DECISIONS if d['id']=='RR_civic_schooling')
d.update(name='整顿教产与学校',summary='75政治点，60天；精神升级为稳定度0、战争支持度−5%、科研速度+3%、适役人口系数+5%、每日政治点+0.05、法律成本−5%；开放希耶里亚的决议。',description='圣像之争已经进入教产与教育的日常管理。皇帝要求清点账册，将部分收入用于学校，并明确教会与官署的职责。新的秩序必须靠持续治理赢得接受。')
loc(d['id'],d['name']);loc(d['id']+'_desc',d['description'])
loc('RR_civic_education','整顿教产与学校已完成')
for f in FOCUSES:loc(f['id'],f['name'])
# Stronger payoff for the disruptive iconoclast route; retain initial penalties.
for i,pp,rs,law,mob in [(2,.10,.03,-.10,.05),(3,.20,.06,-.10,.10),(4,.30,.10,-.15,.15)]:
    IDEAS['RR_identity'+str(i)].update(political_power_gain=pp,research_speed_factor=rs,laws_cost=law,mobilization_speed=mob)
node('roman_community')['summary']='圣像整顿精神升级至：稳定度+10%、战争支持度+5%、科研速度+6%、适役人口系数+15%、每日政治点+0.20、法律成本−10%、动员速度+10%。'
node('citizen_above_creed')['summary']='圣像整顿精神最终：稳定度+15%、战争支持度+10%、科研速度+10%、适役人口系数+25%、每日政治点+0.30、法律成本−15%、动员速度+15%。'
next(d for d in DECISIONS if d['id']=='RR_civic_schooling')['summary']='75政治点，60天；精神升级为稳定度0、战争支持度−5%、科研速度+5%、适役人口系数+5%、每日政治点+0.10、法律成本−10%、动员速度+5%；开放希耶里亚的决议。'