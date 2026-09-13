
event(0,'紫衣重临','将军、学者和流亡者聚集在双头鹰之下。他们所拥戴的君士坦丁十一世将以旧帝国的记忆，为这个现代国家寻找新的道路。复兴已经有了旗帜，接下来需要制度、工业与人民的支持。',[('帝国派正式登场。','',100)])
next(f for f in FOCUSES if f['id']=='RR_empire')['reward'] += ' country_event = { id = rr.0 }'
event(1,'帝国问题','帝国复兴纲领公布已有三十五日。军官、教会与市民代表终于坐到一起：帝国应以公投恢复王冠，还是由执政官领导运动夺取权力？无论选择何者，旧秩序都已不能回应这个国家的愿望。',[
 ('王冠与双头鹰。','RR_issue_common = yes add_stability = .05 '+setflag('crown'),50),
 ('执政官将成为巴西琉斯。','RR_issue_common = yes add_stability = -.05 '+setflag('basileus'),50)])
event(2,'国民的裁决','选票已经清点完毕。支持复兴的声音汇聚为新的授权，君士坦丁十一世将以皇帝之名承担国家的命运。议会与军队承认结果，接下来必须让承诺变成治理。',[('以人民的授权，迎回紫衣。','',100)])
event(3,'秩序重建','整肃留下的恐惧正在消退。军队重新接受统一指挥，地方官署恢复运作，帝国政府终于能够把注意力从权力争夺转向国家重建。',[('让秩序带来复兴。','if = { limit = { has_government = empire } '+timed('order',365)+' }',100)])
event(5,'来自雅典的正统要求','雅典的帝国政府要求我们承认拜占庭的历史正统，交出东色雷斯、伊斯坦布尔以及划定的爱琴海沿岸地区。使者明确表示，拒绝将意味着立即开战。这不是一封可以无限搁置的照会。',[
 ('土耳其不会向旧帝国低头。','GRE = { declare_war_on = { target = TUR type = annex_everything } '+timed('first_war',180)+' country_event = { id = rr.6 } }',90),
 ('接受协定，避免战争。','\n'.join(f'if = {{ limit = {{ owns_state = {s} }} GRE = {{ transfer_state = {s} }} }}' for s in AEGEAN)+' GRE = { country_event = { id = rr.8 } }',10)])
event(6,'交涉破裂','安卡拉拒绝了帝国的要求。边境部队已经接到命令，第一次光复战争开始了。街头的集会与新征召的队伍表明，故土的记忆仍能动员这个国家。',[('帝国将为自己的要求而战。','',100)])
event(7,'新罗马再临','双头鹰再度俯瞰博斯普鲁斯海峡。政府宣布以拜占庭之名延续国家，安纳托利亚故土也被正式纳入帝国的核心领土纲领。',[('旧日的名字，新的国家。','RR_rename_constantinople = yes',100)])
event(8,'安卡拉接受协定','土耳其政府接受了领土协定。交接委员会将进入东色雷斯与爱琴海沿岸，帝国必须以行政能力证明，它能够治理刚刚接收的土地。',[('让交接有序进行。','',100)])
event(11,'帝国应如何治理','征服不能替代制度。军区官员主张将税收和征兵纳入中央编制，另一批代表则希望以服役义务换取地方经营权。两种安排都能维持帝国，却将塑造不同的国家。',[
 ('中央集权军区制。',setflag('central')+' RR_set_central = yes',50),
 ('新普罗尼亚体系。',setflag('pronoia')+' RR_set_pronoia = yes',50)])
event(12,'帝国宪制确立','将军、行省代表与元老终于在同一份法令上留下姓名。国家不再依赖一次次紧急命令维持统治，皇帝的权威与议会的职责有了明确边界。昔日争夺政府的派系，将在制度之内争论。',[('让争论留在议事厅，让秩序遍及行省。','',100)])
event(13,'罗马帝国的首都','旧罗马与新罗马都已回到同一面旗帜之下。重建帝国的宣告将从哪座城市发出？这个选择不仅关乎历史，也将决定下一轮公共建设和人口投入的方向。',[
 ('君士坦丁堡仍是帝国之心。','RR_proclaim_rome = yes set_capital = { state = 797 } RR_rename_constantinople = yes '+buildings(797,'industrial_complex',2,3)+buildings(797,'infrastructure',1)+' 797 = { remove_dynamic_modifier = RR_capital_base add_dynamic_modifier = { modifier = RR_capital_imperial } }',50),
 ('让元老院与人民重返罗马。','RR_proclaim_rome = yes set_capital = { state = 2 } '+buildings(2,'industrial_complex',3,4)+buildings(2,'infrastructure',1)+' 2 = { add_dynamic_modifier = { modifier = RR_capital_rome } }',50)])
event(14,'国家教育体系建立','从地方学校到帝国大学，新的课程、教师训练和教育行政终于连成一个体系。它不会在一夜之间改变社会，但每一届学生都将使国家更有能力理解和运用现代科学。',[('让知识成为公民共同的财富。','',100)])
event(15,'国家实验室的研究方向','筹备工作已经完成。研究委员会建议集中有限的设备与人员，先建成一座能够承担特别项目的实验设施。',[('优先陆战研究。','RR_build_land_lab = yes',34),('优先海军研究。','RR_build_naval_lab = yes',33),('优先航空研究。','RR_build_air_lab = yes',33)])
event(20,'西部帝冠协定','拜占庭提出一项帝冠协定：意大利接受帝国宗主权，保留地方行政，并以协商方式纳入新的罗马秩序。拒绝将使双方的历史争论转化为军事对抗。',[
 ('意大利不会交出自己的主权。','GRE = { '+wargoal('ITA')+' }',90),
 ('接受协定，保留地方行政。','GRE = { puppet = ITA }',10)])
EFFECTS['RR_issue_common']='add_political_power = 75 RR_set_movement3 = yes '+idea('consensus')+' add_to_variable = { GRE_monarchist_loyalty = 1 }'
EFFECTS['RR_research_slot']='if = { limit = { num_research_slots < 6 } add_research_slot = 1 }'
EFFECTS['RR_rename_constantinople']='797 = { set_state_name = RR_constantinople } set_province_name = { id = 9833 name = RR_constantinople }'
EFFECTS['RR_proclaim_rome']='set_cosmetic_tag = RR_ROM '+setflag('rome_proclaimed')
EFFECTS['RR_take_power']='''set_politics = { ruling_party = empire elections_allowed = no }
promote_character = { character = RR_constantine ideology = roman_restoration }
set_party_name = { ideology = empire name = RR_empire_party long_name = RR_empire_party }
remove_ideas = GRE_metaxism remove_ideas = GRE_metaxism_2 remove_ideas = GRE_metaxism_3
remove_ideas = GRE_george_ii remove_ideas = GRE_george_ii_restrained
if = { limit = { is_in_faction = yes is_faction_leader = no } leave_faction = yes }
set_rule = { can_create_factions = no }'''
EFFECTS['RR_emperor_administration']='RR_constantine = { add_country_leader_trait = RR_imperial_administrator }'
instability_ids=re.findall(r'(?m)^\s*(GRE_political_instability\w*)\s*=\s*\{',read('common/ideas/greece.txt'))
EFFECTS['RR_end_instability']='\n'.join('remove_ideas = '+x for x in instability_ids)+'\n'+setflag('constitution_done')+' '+idea('senate')
for kind in ['land','naval','air']:
    EFFECTS['RR_build_'+kind+'_lab']=f'''if = {{ limit = {{ any_owned_state = {{ is_controlled_by = ROOT free_building_slots = {{ building = {kind}_facility size > 0 include_locked = yes }} }} }}
    random_owned_controlled_state = {{ limit = {{ free_building_slots = {{ building = {kind}_facility size > 0 include_locked = yes }} }}
    add_building_construction = {{ type = {kind}_facility level = 1 instant_build = yes }} }} }}
    else = {{ add_political_power = 100 clr_country_flag = RR_national_laboratory_taken }}'''
loc('RR_constantinople','君士坦丁堡')
loc('RR_imperial_concord','帝国协约')
loc('RR_empire_party','帝国派')
loc('RR_research_bonus','帝国研究计划')

# State modifiers, not global national spirits.
dynamic=[]
for key,name,build,mp,defense in [('base','皇都建设',.1,.1,.05),('imperial','帝国之心',.15,.2,.1),('rome','永恒之城',.2,.3,.1)]:
    loc('RR_capital_'+key,name)
    dynamic.append(f'''RR_capital_{key} = {{ enable = {{ always = yes }}
        state_production_speed_buildings_factor = {build}
        local_manpower = {mp}
        local_defence = {defense}
    }}''')
write('common/dynamic_modifiers/rr_capitals.txt','\n'.join(dynamic))

