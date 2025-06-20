# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# data_loader.py - 데이터 로딩 및 정의
# ==============================================================================

"""
Data loading module for T-GCSM v2.0
Loads all necessary CSV data for the simulation using io.StringIO.
"""

import pandas as pd
import io


def load_data():
    """
    Load all simulation data from embedded CSV strings.
    
    Returns:
        dict: Dictionary containing all dataframes needed for simulation
    """
    data_files = {}

    # --- 부록 A: 대만 헥스 맵 데이터 ---
    hex_map_csv = """hex_id,name,terrain_type,is_port,port_name,is_airfield,airfield_name,is_victory_point,initial_owner
A1,North Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
A2,North Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
A3,North Hills,Hills,FALSE,,FALSE,,FALSE,ROC
A4,North Hills,Hills,FALSE,,FALSE,,FALSE,ROC
A5,North Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
A6,North Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
A7,North Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
A8,Yilan Plain,Plains,FALSE,,TRUE,Ilan Airport,FALSE,ROC
A9,Keelung,Urban,TRUE,Port of Keelung,FALSE,,FALSE,ROC
A10,Taipei,Urban,TRUE,Port of Taipei,TRUE,Taipei Songshan Airport,TRUE,ROC
A11,New Taipei,Urban,FALSE,,FALSE,,FALSE,ROC
A12,Matsu Islands,Coastal,TRUE,Fuao Harbor,TRUE,Matsu Beigan Airport,FALSE,ROC
A13,Kinmen Islands,Coastal,TRUE,Shuitou Pier,TRUE,Kinmen Airport,FALSE,ROC
B1,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
B2,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
B3,Hsinchu Hills,Hills,FALSE,,FALSE,,FALSE,ROC
B4,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
B5,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
B6,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
B7,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
B8,Yilan,Urban,FALSE,,FALSE,,FALSE,ROC
B9,Taipei Basin,Plains,FALSE,,FALSE,,FALSE,ROC
B10,Taoyuan,Plains,FALSE,,TRUE,Taiwan Taoyuan Intl Airport,FALSE,ROC
B11,Linkou Plateau,Hills,FALSE,,FALSE,,FALSE,ROC
B12,North Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
B13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
C1,Penghu Channel,Ocean,FALSE,,FALSE,,FALSE,ROC
C2,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
C3,Miaoli Hills,Hills,FALSE,,FALSE,,FALSE,ROC
C4,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
C5,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
C6,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
C7,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
C8,East Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
C9,Hualien Valley,Plains,FALSE,,FALSE,,FALSE,ROC
C10,Hsinchu,Urban,FALSE,,TRUE,Hsinchu AB,FALSE,ROC
C11,Taoyuan Plateau,Hills,FALSE,,FALSE,,FALSE,ROC
C12,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
C13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
D1,Penghu Channel,Ocean,FALSE,,FALSE,,FALSE,ROC
D2,West Coast,Coastal,TRUE,Port of Taichung,FALSE,,FALSE,ROC
D3,Taichung Basin,Plains,FALSE,,FALSE,,FALSE,ROC
D4,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
D5,Taichung,Urban,FALSE,,TRUE,Taichung Intl Airport,FALSE,ROC
D6,Central Mt.,Mountain,FALSE,,FALSE,,FALSE,ROC
D7,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
D8,East Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
D9,East Rift Valley,Plains,FALSE,,FALSE,,FALSE,ROC
D10,Changhua,Plains,FALSE,,FALSE,,FALSE,ROC
D11,Yunlin,Plains,FALSE,,FALSE,,FALSE,ROC
D12,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
D13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
E1,Penghu Islands,Coastal,TRUE,Magong Harbor,TRUE,Penghu Airport,FALSE,ROC
E2,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
E3,Chiayi Hills,Hills,FALSE,,FALSE,,FALSE,ROC
E4,Alishan,Mountain,FALSE,,FALSE,,FALSE,ROC
E5,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
E6,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
E7,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
E8,East Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
E9,East Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
E10,Chiayi,Urban,FALSE,,TRUE,Chiayi Airport,FALSE,ROC
E11,Tainan Plains,Plains,FALSE,,FALSE,,FALSE,ROC
E12,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
E13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
F1,Taiwan Strait,Ocean,FALSE,,FALSE,,FALSE,ROC
F2,Anping,Coastal,TRUE,Port of Anping,FALSE,,FALSE,ROC
F3,Tainan,Urban,FALSE,,TRUE,Tainan Airport,FALSE,ROC
F4,Zhuoshui River,River_Crossing,FALSE,,FALSE,,FALSE,ROC
F5,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
F6,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
F7,Central Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
F8,East Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
F9,East Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
F10,Tainan County,Plains,FALSE,,FALSE,,FALSE,ROC
F11,Kaohsiung Plains,Plains,FALSE,,FALSE,,FALSE,ROC
F12,West Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
F13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
G1,Taiwan Strait,Ocean,FALSE,,FALSE,,FALSE,ROC
G2,Kaohsiung,Urban,TRUE,Port of Kaohsiung,TRUE,Kaohsiung Intl Airport,FALSE,ROC
G3,Fengshan,Urban,FALSE,,FALSE,,FALSE,ROC
G4,Pingtung Plains,Plains,FALSE,,FALSE,,FALSE,ROC
G5,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
G6,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
G7,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
G8,Taitung Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
G9,Taitung,Urban,FALSE,,TRUE,Taitung Airport,FALSE,ROC
G10,Green Island,Coastal,FALSE,,TRUE,Lyudao Airport,FALSE,ROC
G11,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
G12,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
G13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
H1,Taiwan Strait,Ocean,FALSE,,FALSE,,FALSE,ROC
H2,South Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
H3,Pingtung,Urban,FALSE,,TRUE,Pingtung South AB,FALSE,ROC
H4,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
H5,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
H6,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
H7,East Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
H8,East Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
H9,Hualien,Urban,TRUE,Port of Hualien,TRUE,Hualien AB,FALSE,ROC
H10,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
H11,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
H12,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
H13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
I1,Bashi Channel,Ocean,FALSE,,FALSE,,FALSE,ROC
I2,Hengchun Peninsula,Coastal,FALSE,,TRUE,Hengchun Airport,FALSE,ROC
I3,Kenting,Hills,FALSE,,FALSE,,FALSE,ROC
I4,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
I5,South Mountains,Mountain,FALSE,,FALSE,,FALSE,ROC
I6,East Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
I7,East Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
I8,East Coast,Coastal,FALSE,,FALSE,,FALSE,ROC
I9,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
I10,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
I11,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
I12,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
I13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J1,Bashi Channel,Ocean,FALSE,,FALSE,,FALSE,ROC
J2,South Cape,Coastal,FALSE,,FALSE,,FALSE,ROC
J3,Orchid Island,Coastal,FALSE,,TRUE,Lanyu Airport,FALSE,ROC
J4,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J5,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J6,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J7,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J8,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J9,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J10,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J11,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J12,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
J13,Offshore,Ocean,FALSE,,FALSE,,FALSE,ROC
"""
    data_files['hex_map'] = pd.read_csv(io.StringIO(hex_map_csv))

    # --- 부록 B: 마스터 장비 카탈로그 ---
    equipment_catalog_csv = """equipment_id,faction,name,type,main_gun_mm,has_atgm,armor_rating,engine_hp,weight_tonnes,max_speed_kph,amphibious_speed_kph,lift_cost
PLA_ZTZ99A,PLA,Type 99A,MBT,125,TRUE,9,1500,55,76,0,10
PLA_ZBD04A,PLA,Type 04A,IFV,100,TRUE,6,670,24,75,8,5
PLA_ZTD05,PLA,Type 05,Amphibious_Assault_Gun,105,TRUE,5,1475,26.5,65,28,6
PLA_ZBD05,PLA,Type 05,Amphibious_IFV,30,TRUE,4,1475,26.5,65,28,6
PLA_PLZ07,PLA,Type 07,SPH,122,FALSE,3,600,22,65,6,5
PLA_PHZ11,PLA,Type 11,MLRS,122,FALSE,3,450,20,90,0,4
ROC_M60A3,ROC,M60A3 TTS,MBT,105,FALSE,6,750,54.6,48,0,0
ROC_CM11,ROC,CM-11 Brave Tiger,MBT,105,FALSE,7,750,50,48,0,0
ROC_CM34,ROC,CM-34 Clouded Leopard,IFV,30,FALSE,5,450,24,120,0,0
ROC_M109A5,ROC,M109A5,SPH,155,FALSE,2,440,29,56,0,0
ROC_M110A2,ROC,M110A2,SPH,203,FALSE,1,405,28,55,0,0
"""
    data_files['equipment_catalog'] = pd.read_csv(io.StringIO(equipment_catalog_csv))

    # --- 부록 C: 표준 대대 템플릿 ---
    battalion_templates_csv = """template_id,faction,unit_type,equipment_id,quantity
PLA_AMPH_ARM_BN,PLA,Armor,PLA_ZTD05,31
PLA_AMPH_ARM_BN,PLA,Armor,PLA_ZBD05,10
PLA_AMPH_MECH_BN,PLA,Mechanized,PLA_ZBD05,42
PLA_ARTY_SPH_BN,PLA,Artillery,PLA_PLZ07,18
PLA_ARTY_MLRS_BN,PLA,Artillery,PLA_PHZ11,18
PLA_AIRBORNE_BN,PLA,Infantry,NULL,0
PLA_ENGINEER_BN,PLA,Engineer,NULL,0
PLA_ATTACK_HELO_BN,PLA,AttackHelo,NULL,0
ROC_ARM_BN_M60,ROC,Armor,ROC_M60A3,44
ROC_ARM_BN_CM11,ROC,Armor,ROC_CM11,44
ROC_MECH_BN_CM34,ROC,Mechanized,ROC_CM34,42
ROC_INF_BN,ROC,Infantry,NULL,0
ROC_ARTY_BN_155,ROC,Artillery,ROC_M109A5,18
ROC_ARTY_BN_203,ROC,Artillery,ROC_M110A2,18
"""
    data_files['battalion_templates'] = pd.read_csv(io.StringIO(battalion_templates_csv), na_values=['NULL'])

    # --- 부록 D: 전체 전투 서열 데이터 ---
    oob_pla_reinforcements_csv = """unit_id,brigade,template_id,initial_strength,location_hex_id,is_reserve,lift_cost
PLA_AMPH_1_BN1,1st Amphibious Brigade,PLA_AMPH_ARM_BN,100,,FALSE,80
PLA_AMPH_1_BN2,1st Amphibious Brigade,PLA_AMPH_MECH_BN,100,,FALSE,40
PLA_AMPH_1_BN3,1st Amphibious Brigade,PLA_AMPH_MECH_BN,100,,FALSE,40
PLA_AMPH_2_BN1,2nd Amphibious Brigade,PLA_AMPH_ARM_BN,100,,FALSE,80
PLA_AMPH_2_BN2,2nd Amphibious Brigade,PLA_AMPH_MECH_BN,100,,FALSE,40
PLA_AMPH_2_BN3,2nd Amphibious Brigade,PLA_AMPH_MECH_BN,100,,FALSE,40
PLA_ARTY_BN1,Artillery Regiment,PLA_ARTY_SPH_BN,100,,FALSE,30
PLA_ARTY_BN2,Artillery Regiment,PLA_ARTY_MLRS_BN,100,,FALSE,25
PLA_AIRBORNE_BN1,Airborne Division,PLA_AIRBORNE_BN,100,,FALSE,20
PLA_AIRBORNE_BN2,Airborne Division,PLA_AIRBORNE_BN,100,,FALSE,20
PLA_ENGINEER_BN1,Engineer Regiment,PLA_ENGINEER_BN,100,,FALSE,15
PLA_HELO_BN1,Army Aviation Brigade,PLA_ATTACK_HELO_BN,100,,FALSE,35
"""
    data_files['oob_pla_reinforcements'] = pd.read_csv(io.StringIO(oob_pla_reinforcements_csv))

    oob_roc_initial_setup_csv = """unit_id,brigade,template_id,initial_strength,location_hex_id,is_reserve,lift_cost
ROC_ARM_542_BN1,542nd Armor Brigade,ROC_ARM_BN_CM11,100,B10,FALSE,0
ROC_ARM_542_BN2,542nd Armor Brigade,ROC_ARM_BN_M60,100,B10,FALSE,0
ROC_ARM_586_BN1,586th Armor Brigade,ROC_ARM_BN_CM11,100,D5,FALSE,0
ROC_MECH_BN1,Mechanized Infantry,ROC_MECH_BN_CM34,100,A10,FALSE,0
ROC_MECH_BN2,Mechanized Infantry,ROC_MECH_BN_CM34,100,E10,FALSE,0
ROC_MECH_BN3,Mechanized Infantry,ROC_MECH_BN_CM34,100,G2,FALSE,0
ROC_INF_BN1,Regular Infantry,ROC_INF_BN,100,C10,FALSE,0
ROC_INF_BN2,Regular Infantry,ROC_INF_BN,100,F3,FALSE,0
ROC_INF_BN3,Regular Infantry,ROC_INF_BN,100,H9,FALSE,0
ROC_INF_R_TPE1,Reserve Infantry,ROC_INF_BN,80,A10,TRUE,0
ROC_INF_R_TPE2,Reserve Infantry,ROC_INF_BN,80,A11,TRUE,0
ROC_INF_R_TYN,Reserve Infantry,ROC_INF_BN,80,B10,TRUE,0
ROC_INF_R_TCG1,Reserve Infantry,ROC_INF_BN,80,D5,TRUE,0
ROC_INF_R_TCG2,Reserve Infantry,ROC_INF_BN,80,E5,TRUE,0
ROC_INF_R_TNN,Reserve Infantry,ROC_INF_BN,80,F3,TRUE,0
ROC_INF_R_KHH1,Reserve Infantry,ROC_INF_BN,80,G2,TRUE,0
ROC_INF_R_KHH2,Reserve Infantry,ROC_INF_BN,80,G3,TRUE,0
ROC_INF_R_PTG,Reserve Infantry,ROC_INF_BN,80,H3,TRUE,0
ROC_ARTY_BN1,Artillery Command,ROC_ARTY_BN_155,100,C11,FALSE,0
ROC_ARTY_BN2,Artillery Command,ROC_ARTY_BN_203,100,E11,FALSE,0
"""
    data_files['oob_roc_initial_setup'] = pd.read_csv(io.StringIO(oob_roc_initial_setup_csv))

    # --- 부록 E: 핵심 메커니즘 데이터 ---
    terrain_modifiers_csv = """terrain_type,movement_cost_factor,defense_multiplier
Plains,1.0,1.0
Hills,2.0,1.5
Mountain,4.0,1.8
Urban,2.0,2.0
Forest,1.5,1.3
River_Crossing,3.0,1.1
Coastal,1.0,1.0
Ocean,99.0,1.0
"""
    data_files['terrain_modifiers'] = pd.read_csv(io.StringIO(terrain_modifiers_csv))

    combat_results_table_csv = """d20_Roll,1:2,1:1,2:1,3:1,4:1+
1-5,A-30/D-0,A-20/D-10,A-10/D-20,A-10/D-30,A-0/D-30
6-10,A-20/D-0,A-10/D-10,A-10/D-20_DR,A-10/D-20_DR,A-0/D-20_DR
11-15,A-10/D-0,A-10/D-10_DR,A-0/D-30_DR,A-0/D-40_DR,A-0/D-50_DR
16-19,A-10/D-0_AR,A-0/D-20_DR,A-0/D-40_DR,A-0/D-50_DR,A-0/D-60_DR
20,A-0/D-0_AX,A-0/D-30_DX,A-0/D-50_DX,A-0/D-60_DX,A-0/D-70_DX
"""
    data_files['combat_results_table'] = pd.read_csv(io.StringIO(combat_results_table_csv))

    return data_files