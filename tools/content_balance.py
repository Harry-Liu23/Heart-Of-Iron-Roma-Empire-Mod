
# Approved numerical/event changes only. All existing focus names and times stay unchanged.
def node(key):
    return next(f for f in FOCUSES if f['id']==fid(key))

IDEAS['RR_cultural_debate']['political_power_gain']=.1
spirit('public_lectures','公开讲学',{'political_power_gain':.1})
node('wisdom_focus')['reward'] += ' country_event = { id = rr.30 }'
node('wisdom_focus')['summary']='稳定度+5、科研速度+5%；600天每日政治点+0.10；事件选择1次工业技术50%研究加成，或600天额外每日政治点+0.10。'
event(30,'书斋与广场','整理古籍的学者和主持公开讲学的教师都请求得到支持。前者希望将旧知识转化为现代研究，后者希望让更多公民理解复兴的共同事业。国家可以维持基础经费，但这一次专项拨款必须确定重点。',[
 ('支持校勘与研究。',bonus('industry'),50),
 ('让知识走向公众。',timed('public_lectures',600),50)])

IDEAS['RR_standards']={'production_factory_efficiency_gain_factor':.03,'line_change_production_efficiency_factor':.05}
node('standardization')['summary']='生产效率增长+3%、生产效率保持+5%；生产、电子技术各1次50%研究加成。'

node('scholars')['reward']='country_event = { id = rr.31 }'
node('scholars')['summary']='开放大学总监；事件选择1次电子技术50%研究加成或1次工业技术50%研究加成。'
event(31,'归国学者的研究方向','归来的学者带来了手稿、实验记录和在海外积累的经验。有人希望先建立电子与通信研究团队，另一些人则主张把有限经费用于工业工程。两条道路都能服务复兴，现在需要确定第一笔拨款的用途。',[
 ('支持电子与通信研究。',bonus('electronics'),50),
 ('支持工业工程研究。',bonus('industry'),50)])

spirit('tourism_merchants','旅游业：商旅与集市',{'stability_factor':.1,'political_power_factor':.15,'consumer_goods_factor':-.1},'和平时期生效：稳定度+10、政治点获取+15%、消费品工厂系数−10%。')
spirit('tourism_pilgrims','旅游业：朝圣与地方建设',{'stability_factor':.1,'consumer_goods_factor':-.15},'和平时期生效：稳定度+10、消费品工厂系数−15%；自有岛州基础设施建设速度+10%。')
node('tourism')['reward']=node('tourism')['reward'].replace('add_ideas = GRE_booming_tourism','country_event = { id = rr.32 }')
node('tourism')['summary']='一次性稳定度+5；外国垄断惩罚降至+10%；事件选择和平旅游方案：商旅为稳定度+10、政治点获取+15%、消费品系数−10%；地方建设为稳定度+10、消费品系数−15%、自有岛州基础设施建设+10%。'
event(32,'旅人带来了什么？','港口迎来了商人、学者与朝圣者。旅馆和市场希望把新客流转化为贸易，地方官署则建议把收入投入岛屿道路与公共设施。旅游的繁荣有赖于和平，而如何使用它的收益，将由我们决定。',[
 ('发展商旅与集市。',setflag('tourism_merchants')+' clr_country_flag = RR_tourism_pilgrims RR_refresh_tourism = yes',50),
 ('支持朝圣与地方建设。',setflag('tourism_pilgrims')+' clr_country_flag = RR_tourism_merchants RR_refresh_tourism = yes',50)])
tourism_states=[187,182,183,164]
setup='\n'.join(f'''{state} = {{ if = {{ limit = {{ is_owned_by = ROOT is_controlled_by = ROOT NOT = {{ has_dynamic_modifier = RR_island_infrastructure }} }}
 add_dynamic_modifier = {{ modifier = RR_island_infrastructure }} }} }}''' for state in tourism_states)
EFFECTS['RR_refresh_tourism']='''if = { limit = { has_war = no }
 if = { limit = { has_country_flag = RR_tourism_merchants }
   remove_ideas = RR_tourism_pilgrims
   if = { limit = { NOT = { has_idea = RR_tourism_merchants } } add_ideas = RR_tourism_merchants }
 }
 else_if = { limit = { has_country_flag = RR_tourism_pilgrims }
   remove_ideas = RR_tourism_merchants
   if = { limit = { NOT = { has_idea = RR_tourism_pilgrims } } add_ideas = RR_tourism_pilgrims }
 '''+setup+'''
 }
}
else = { remove_ideas = RR_tourism_merchants remove_ideas = RR_tourism_pilgrims }'''
p=ROOT/'common/dynamic_modifiers/rr_capitals.txt'
write(str(p.relative_to(ROOT)),p.read_text(encoding='utf-8')+'''
RR_island_infrastructure = {
 enable = { is_owned_by = GRE is_controlled_by = GRE
   owner = { has_country_flag = RR_tourism_pilgrims has_war = no } }
 state_production_speed_infrastructure_factor = .1
}
''')
loc('RR_island_infrastructure','旅游业地方建设')

spirit('farmland_common','马其顿农业与粮运',{'attrition':-.05,'supply_consumption_factor':-.05,'supply_combat_penalties_on_core_factor':-.1,'supply_node_range':.1})
spirit('farmland_tax','马其顿田籍：税粮入仓',{'consumer_goods_factor':-.05})
spirit('farmland_service','马其顿田籍：登记军户',{'conscription_factor':.05})
node('farmlands')['reward']=idea('farmland_common')+' country_event = { id = rr.33 }'
node('farmlands')['summary']='损耗−5%、补给消耗−5%、核心补给战斗惩罚−10%、补给范围+10%；事件选择消费品工厂系数−5%，或适役人口系数+5%。'
event(33,'田籍上的人民','田籍已经完成整理。财政官希望以更稳定的税粮供应减轻国库负担，军务官则建议在保障土地经营的同时登记可供征召的军户。新增的行政能力足以推进其中一项改革。',[
 ('先让税粮进入仓库。','remove_ideas = RR_farmland_service '+idea('farmland_tax'),50),
 ('登记军户，准备服役。','remove_ideas = RR_farmland_tax '+idea('farmland_service'),50)])

spirit('case_review','清理积案',{'resistance_growth':-.1,'compliance_growth':.02},'120天：抵抗增长−10%、每日顺从度增长+0.02。')
decision('clear_cases','清理积案',75,30,done('codex'),'NOT = { has_idea = RR_case_review }',
 timed('case_review',120),'75政治点、准备30天；随后120天抵抗增长−10%、每日顺从度增长+0.02；效果结束后冷却240天。',once=False,cooldown=360)
node('codex')['summary']='开放大法官：任用时法律与政治顾问成本−15%、意识形态变化抵制+25%；开放75政治点的清理积案临时治理决议。'

