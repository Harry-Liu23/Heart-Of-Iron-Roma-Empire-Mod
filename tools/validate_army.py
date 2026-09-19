"""Army regression checks, run inside validate_mod.py's validation context."""
import itertools

def army_parse(source):
    tokens=re.findall(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[<>]=?|[^\s{}=<>]+',source)
    tokens=[t for t in tokens if not t.startswith('#')]
    pos=0
    def seq(nested=False):
        nonlocal pos
        out=[]
        while pos<len(tokens):
            key=tokens[pos]; pos+=1
            if key=='}':
                if not nested:raise ValueError('unexpected closing brace')
                return out
            if pos<len(tokens) and tokens[pos] in ['=','<','>','<=','>=']:
                op=tokens[pos]; pos+=1
                value=tokens[pos]; pos+=1
                if value=='{':value=seq(True)
                out.append((key,op,value))
            else:out.append((key,None,None))
        if nested:raise ValueError('missing closing brace')
        return out
    return seq()

def av(nodes,key,default=None):
    return next((v for k,o,v in nodes if k==key),default)

def ab(nodes,key):
    return av(nodes,key,[])

army=manifest['army']
infantry=army['infantry']; armor=army['armor']; final=army['final']
check(army['entry']=='RR_empire','army entry must remain early-game')
for branch in [infantry,armor]:
    check(sum(focuses[k]['days'] for k in branch)==112,'independent branch 112-day duration')
    for i,key in enumerate(branch):
        f=focuses[key]
        check(f['parents']==[[branch[i-1] if i else 'RR_empire']],key+' independent prerequisite')
        check(not f['mutex'] and not f['bypass'],key+' has no exclusivity or reward-skipping bypass')
        check('has_completed_focus' not in f['available'],key+' has no hidden focus gate')
check(focuses[final]['parents']==[[infantry[-1]],[armor[-1]]],'final requires BOTH branch endpoints')
check(sum(focuses[k]['days'] for k in infantry+armor+[final])==259,'full army 259-day duration')
coords=[(f['x'],f['y']) for f in manifest['focuses']]
check(len(coords)==len(set(coords)),'no custom focus layout overlap')
check('num_divisions > 7'==focuses[infantry[1]]['available'],'military themes requires eight divisions')
for key in [infantry[2],armor[2]]:
    check(focuses[key]['available']=='num_of_military_factories > 2',key+' industry prerequisite')

idea_nodes=ab(army_parse(text(ROOT/'common/ideas/rr_spirits.txt')),'ideas')
idea_nodes=ab(idea_nodes,'country')
for key,categories in [('RR_marian_reform_spirit',{'infantry_weapons','artillery'}),('RR_cataphract_research_spirit',{'armor'})]:
    bonus=ab(ab(idea_nodes,key),'research_bonus')
    check({k for k,o,v in bonus}==categories,key+' research categories')
    check(all(float(v)==.05 for k,o,v in bonus),key+' permanent research 5 percent')
reward=army_parse(focuses['RR_recast_cataphracts']['reward'])
bonus=ab(reward,'add_tech_bonus')
check(av(bonus,'category')=='armor' and av(bonus,'uses')=='2' and float(av(bonus,'bonus'))==.5,'two 50-percent tank research awards')
marian_bonus=[v for k,o,v in army_parse(focuses[infantry[0]]['reward']) if k=='add_tech_bonus']
check({av(v,'category') for v in marian_bonus}=={'infantry_weapons','artillery'},'no support-company research award')
for key in ['RR_imperial_workshops_spirit','RR_modern_cataphracts_spirit']:
    eq=ab(ab(idea_nodes,key),'equipment_bonus')
    check({k for k,o,v in eq}=={'armor','armored_car_equipment'},key+' covers tanks and armored cars without double bonuses')
    for cat,o,mods in eq:
        check(av(mods,'instant')=='yes',key+' applies to existing equipment')
        check(av(mods,'breakthrough') is None,key+' has no breakthrough bonus')
        if 'modern' in key:
            check({k:float(v) for k,o,v in mods if k!='instant'}=={'maximum_speed':.1,'soft_attack':.15,'hard_attack':.15,'defense':.15},'cataphract equipment stats')
        else:check(float(av(mods,'build_cost_ic'))==-.15,'vehicle cost reduction')
legion=ab(army_parse(focuses['RR_roman_legions']['reward']),'add_unit_bonus')
check({k for k,o,v in legion}=={'infantry','artillery','artillery_brigade'},'legions excludes motorized and self-propelled artillery')
check(av(ab(legion,'infantry'),'max_organisation')=='10','legion organization +10')
for key in infantry+armor+[final]:
    check('set_technology' not in focuses[key]['reward'],key+' no hidden special technology')

chars=ab(army_parse(text(ROOT/'common/characters/rr_court.txt')),'characters')
for t in army['theorists']:
    person=ab(chars,t['character'])
    roles=[v for k,o,v in person if k=='advisor']
    check(len({av(v,'slot') for v in roles})==len(roles),t['character']+' unique advisor slots')
    role=next(v for v in roles if av(v,'slot')=='theorist')
    check(av(role,'idea_token')==t['token'] and av(role,'cost')=='100','theorist idea token and cost')
    check(av(ab(role,'available'),'has_completed_focus')==t['unlock'],'theorist unlock focus')
    check({k:float(v) for k,o,v in ab(role,'research_bonus')}==t['research'],'theorist category research')
    commander=ab(person,'corps_commander') or ab(person,'field_marshal')
    check('brilliant_strategist' in {k for k,o,v in ab(commander,'traits')},t['character']+' remains brilliant strategist')
    check(t['trait'] not in {k for k,o,v in ab(commander,'traits')},'theorist is not a general trait')
    check(t['token'] in locids and t['trait'] in locids,'theorist localization')

fx=army_parse(effects)
upgrade=ab(fx,'RR_upgrade_marian_minister')
check(av(ab(ab(upgrade,'if'),'limit'),'has_idea')=='RR_belisarius','preserve minister activation only if previously employed')
for branch in ['if','else']:
    body=ab(upgrade,branch)
    remove=ab(body,'remove_advisor_role'); add=ab(body,'add_advisor_role')
    check(av(remove,'character')=='RR_belisarius' and av(remove,'slot')=='army_chief','upgrade only existing Belisarius chief role')
    check(av(add,'character')=='RR_belisarius','upgrade preserves character')
    check(av(ab(add,'advisor'),'cost')=='75','new minister 75 PP')
    check(av(add,'activate')==('yes' if branch=='if' else None),'no displacement of another serving chief')
check(av(ab(ab(chars,'RR_heraclius'),'advisor'),'slot')=='high_command','original armored high-command role retained')

# Exercise the generated reward script, rather than a second copy of its logic.
settlement=ab(fx,'RR_settle_army_mio_rewards')
class ArmyRewardState:
    def __init__(self):
        self.flags=set(); self.control=set(); self.dlc=True; self.funds={}; self.research={}
    def condition(self,nodes):
        result=[]
        for key,op,val in nodes:
            if key=='NOT':result.append(not self.condition(val))
            elif key=='has_dlc':result.append(self.dlc)
            elif key=='has_country_flag':result.append(val in self.flags)
            elif key=='controls_state':result.append(int(val) in self.control)
            else:raise AssertionError('Unhandled reward condition '+key)
        return all(result)
    def execute(self,nodes,mio=None):
        for key,op,val in nodes:
            if key=='if':
                if self.condition(ab(val,'limit')):self.execute([n for n in val if n[0]!='limit'],mio)
            elif key.startswith('mio:'):self.execute(val,key[4:])
            elif key=='set_country_flag':self.flags.add(val)
            elif key=='add_mio_funds':self.funds[mio]=self.funds.get(mio,0)+int(val)
            elif key=='add_mio_research_bonus':self.research[mio]=self.research.get(mio,0)+float(val)
            else:raise AssertionError('Unhandled reward effect '+key)

expected_funds={'RR_mio_piraeus':1500,'RR_mio_ankara_armor':1500,'RR_mio_thessaloniki':500}
for order in itertools.permutations(['state_armories','imperial_workshops','roman_military_glory']):
    state=ArmyRewardState()
    for key in order:
        state.flags.add('RR_army_reward_'+key)
        state.execute(settlement)
    check(state.funds=={},'unopened enterprises defer rewards')
    state.flags.add('RR_enterprises')
    state.flags.update(k+'_initialized' for k in expected_funds)
    state.execute(settlement)
    check(state.funds=={},'lost headquarters defer rewards')
    state.control={47,49,731}
    state.execute(settlement)
    check(state.funds==expected_funds,'pending awards paid in either branch order')
    check(state.research=={'RR_mio_piraeus':.1,'RR_mio_ankara_armor':.1},'research only assigned to target MIO')
    for day in range(30):state.execute(settlement)
    state.control=set(); state.execute(settlement)
    state.control={47,49,731}; state.execute(settlement)
    check(state.funds==expected_funds,'daily refresh and recapture cannot duplicate rewards')
    check(state.research=={'RR_mio_piraeus':.1,'RR_mio_ankara_armor':.1},'MIO research cannot stack on refresh')
state=ArmyRewardState(); state.control={47,49,731}; state.dlc=False
state.flags={'RR_enterprises'}|{k+'_initialized' for k in expected_funds}|{'RR_army_reward_'+k for k in ['state_armories','imperial_workshops','roman_military_glory']}
state.execute(settlement)
check(not state.funds and not state.research,'no MIO effects without required DLC')
check('RR_settle_army_mio_rewards = yes' in effects,'enterprise updater retries pending rewards')

mios=army_parse(text(ROOT/'common/military_industrial_organization/organizations/rr_organizations.txt'))
for key in expected_funds:
    mio=ab(mios,key); initial=ab(mio,'initial_trait')
    check(float(av(ab(initial,'equipment_bonus'),'build_cost_ic'))==-.05,key+' initial cost bonus needs no unlock')
    check(float(av(ab(initial,'production_bonus'),'production_capacity_factor'))==.05,key+' retains original production bonus')
check({k for k,o,v in ab(ab(mios,'RR_mio_ankara_armor'),'equipment_type')}=={'armor','armored_car_equipment'},'MIO includes armored cars')
# Check the game's equipment definitions, not an invented list of unit categories.
equipment={}
for path in (GAME/'common/units/equipment').glob('*.txt'):
    parsed=army_parse(text(path))
    for key,op,value in ab(parsed,'equipments')+ab(parsed,'duplicate_archetypes'):
        if isinstance(value,list):equipment[key]=value
for key in ['light_tank_chassis','medium_tank_chassis','heavy_tank_chassis',
            'light_tank_artillery_chassis','medium_tank_destroyer_chassis','heavy_tank_aa_chassis']:
    types=av(equipment.get(key,[]),'type')
    check(types=='armor' or isinstance(types,list) and 'armor' in {k for k,o,v in types},key+' receives armor-type bonus')
check(av(equipment.get('armored_car_equipment',[]),'type')=='motorized','armored cars require explicit separate equipment bonus')