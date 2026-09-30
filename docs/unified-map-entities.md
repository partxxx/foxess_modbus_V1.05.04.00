# Unified map (EXPERIMENTAL): entity reference

Generated from the integration code (`Inv.UNIFIED_3PH` / `Inv.UNIFIED_1PH`). Addresses are holding registers.

_Enabled_: `default` = enabled when created, `disabled` = created disabled (enable it in HA to test it),
`developer` = only created with the _Create raw register entities_ option, and disabled.

Three-phase models: 254 entities; single-phase models: 218 (the rows marked _3-phase only_ are left out).

| Key                                          | Name                                       | Register(s)                              | Scale          | Unit | Signed | Phases       | Enabled   |
| -------------------------------------------- | ------------------------------------------ | ---------------------------------------- | -------------- | ---- | ------ | ------------ | --------- |
| `pv1_energy_total`                           | PV1 Power Total                            | integrated from `pv1_power`              |                | kWh  |        |              | default   |
| `pv2_energy_total`                           | PV2 Power Total                            | integrated from `pv2_power`              |                | kWh  |        |              | default   |
| `pv3_energy_total`                           | PV3 Power Total                            | integrated from `pv3_power`              |                | kWh  |        |              | default   |
| `master_version`                             | Version: Master                            | 36001                                    | decimal digits |      |        |              | default   |
| `slave_version`                              | Version: Slave                             | 36002                                    | decimal digits |      |        |              | default   |
| `manager_version`                            | Version: Manager                           | 36003                                    | hex digits     |      |        |              | default   |
| `bms1_master_version`                        | BMS1 Master Version (37003)                | 37003                                    | decoded text   |      |        |              | disabled  |
| `register_37004_raw`                         | Register 37004 raw                         | 37004                                    |                |      |        |              | developer |
| `register_37032_raw`                         | Register 37032 raw                         | 37032                                    |                |      |        |              | developer |
| `register_37033_raw`                         | Register 37033 raw                         | 37033                                    |                |      |        |              | developer |
| `register_37034_raw`                         | Register 37034 raw                         | 37034                                    |                |      |        |              | developer |
| `batvolt_1`                                  | Battery 1 Voltage                          | 37609                                    | × 0.1          | V    |        |              | disabled  |
| `bat_current_1`                              | Battery 1 Current                          | 37610                                    | × 0.1          | A    | signed |              | disabled  |
| `battery_temp`                               | Battery Temp                               | 37611                                    | × 0.1          | °C   | signed |              | default   |
| `battery_temp_1`                             | Battery 1 Temp                             | 37611                                    | × 0.1          | °C   | signed |              | disabled  |
| `battery_soc`                                | Battery SoC                                | 37612                                    |                | %    |        |              | default   |
| `reg_37615_bms_max_current_candidate`        | BMS Max Current candidate (37615)          | 37615                                    | × 0.1          | A    |        |              | developer |
| `bms_cell_temp_high`                         | BMS Cell Temp High                         | 37617                                    | × 0.1          | °C   | signed |              | default   |
| `bms_cell_temp_high_1`                       | BMS 1 Cell Temp High                       | 37617                                    | × 0.1          | °C   | signed |              | disabled  |
| `bms_cell_temp_low`                          | BMS Cell Temp Low                          | 37618                                    | × 0.1          | °C   | signed |              | default   |
| `bms_cell_temp_low_1`                        | BMS 1 Cell Temp Low                        | 37618                                    | × 0.1          | °C   | signed |              | disabled  |
| `bms_cell_mv_high`                           | BMS Cell mV High                           | 37619                                    |                | mV   |        |              | default   |
| `bms_cell_mv_high_1`                         | BMS 1 Cell mV High                         | 37619                                    |                | mV   |        |              | disabled  |
| `bms_cell_mv_low`                            | BMS Cell mV Low                            | 37620                                    |                | mV   |        |              | default   |
| `bms_cell_mv_low_1`                          | BMS 1 Cell mV Low                          | 37620                                    |                | mV   |        |              | disabled  |
| `battery_soh`                                | Battery SoH                                | 37624                                    |                | %    |        |              | default   |
| `battery_soh_1`                              | Battery 1 SoH                              | 37624                                    |                | %    |        |              | disabled  |
| `reg_37626_bms1_fault1`                      | BMS1 Fault1 (37626)                        | 37626                                    |                |      |        |              | developer |
| `reg_37627_bms1_fault2`                      | BMS1 Fault2 (37627)                        | 37627                                    |                |      |        |              | developer |
| `reg_37628_bms1_fault3`                      | BMS1 Fault3 (37628)                        | 37628                                    |                |      |        |              | developer |
| `reg_37629_bms1_fault4`                      | BMS1 Fault4 (37629)                        | 37629                                    |                |      |        |              | developer |
| `reg_37630_bms1_fault5`                      | BMS1 Fault5 (37630)                        | 37630                                    |                |      |        |              | developer |
| `reg_37631_bms1_fault6`                      | BMS1 Fault6 (37631)                        | 37631                                    |                |      |        |              | developer |
| `bms_kwh_remaining`                          | BMS kWh Remaining                          | 37632                                    | × 0.01         | kWh  |        |              | default   |
| `bms_kwh_remaining_1`                        | BMS 1 kWh Remaining                        | 37632                                    | × 0.01         | kWh  |        |              | disabled  |
| `reg_37633_bms1_fcc_capacity`                | BMS1 FCC Capacity (37633)                  | 37633                                    | × 0.1          | Ah   |        |              | disabled  |
| `reg_37635_bms1_design_energy`               | BMS1 Design Energy (37635)                 | 37635                                    | × 10           | Wh   |        |              | disabled  |
| `register_37636_raw`                         | Register 37636 raw                         | 37636                                    |                |      |        |              | developer |
| `register_38801_raw`                         | Register 38801 raw                         | 38801                                    |                |      |        |              | developer |
| `reg_38802_grid_ct1_r_phase_voltage`         | Grid CT1 R Phase Voltage (38802)           | 38802–38803 (32-bit, high word first)    | × 0.1          | V    | signed |              | disabled  |
| `reg_38804_grid_ct1_s_phase_voltage`         | Grid CT1 S Phase Voltage (38804)           | 38804–38805 (32-bit, high word first)    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `reg_38806_grid_ct1_t_phase_voltage`         | Grid CT1 T Phase Voltage (38806)           | 38806–38807 (32-bit, high word first)    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `reg_38808_grid_ct1_r_phase_current`         | Grid CT1 R Phase Current (38808)           | 38808–38809 (32-bit, high word first)    | × 0.001        | A    | signed |              | disabled  |
| `reg_38810_grid_ct1_s_phase_current`         | Grid CT1 S Phase Current (38810)           | 38810–38811 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `reg_38812_grid_ct1_t_phase_current`         | Grid CT1 T Phase Current (38812)           | 38812–38813 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `feed_in`                                    | Feed-in                                    | 38814–38815 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | disabled  |
| `grid_consumption`                           | Grid Consumption                           | 38814–38815 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | disabled  |
| `grid_ct`                                    | Grid CT                                    | 38814–38815 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | disabled  |
| `feed_in_R`                                  | Feed-in R                                  | 38816–38817 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | default   |
| `grid_consumption_R`                         | Grid Consumption R                         | 38816–38817 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | default   |
| `grid_ct_R`                                  | Grid CT R                                  | 38816–38817 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | default   |
| `feed_in_S`                                  | Feed-in S                                  | 38818–38819 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_consumption_S`                         | Grid Consumption S                         | 38818–38819 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_ct_S`                                  | Grid CT S                                  | 38818–38819 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `feed_in_T`                                  | Feed-in T                                  | 38820–38821 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_consumption_T`                         | Grid Consumption T                         | 38820–38821 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_ct_T`                                  | Grid CT T                                  | 38820–38821 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `reg_38822_grid_ct1_combined_reactive`       | Grid CT1 Combined Reactive (38822)         | 38822–38823 (32-bit, high word first)    | × 0.1          | var  | signed |              | disabled  |
| `reg_38824_grid_ct1_r_phase_reactive`        | Grid CT1 R Phase Reactive (38824)          | 38824–38825 (32-bit, high word first)    | × 0.1          | var  | signed |              | disabled  |
| `reg_38826_grid_ct1_s_phase_reactive`        | Grid CT1 S Phase Reactive (38826)          | 38826–38827 (32-bit, high word first)    | × 0.1          | var  | signed | 3-phase only | disabled  |
| `reg_38828_grid_ct1_t_phase_reactive`        | Grid CT1 T Phase Reactive (38828)          | 38828–38829 (32-bit, high word first)    | × 0.1          | var  | signed | 3-phase only | disabled  |
| `reg_38830_grid_ct1_combined_apparent`       | Grid CT1 Combined Apparent (38830)         | 38830–38831 (32-bit, high word first)    | × 0.1          | VA   | signed |              | disabled  |
| `reg_38832_grid_ct1_r_phase_apparent`        | Grid CT1 R Phase Apparent (38832)          | 38832–38833 (32-bit, high word first)    | × 0.1          | VA   | signed |              | disabled  |
| `reg_38834_grid_ct1_s_phase_apparent`        | Grid CT1 S Phase Apparent (38834)          | 38834–38835 (32-bit, high word first)    | × 0.1          | VA   | signed | 3-phase only | disabled  |
| `reg_38836_grid_ct1_t_phase_apparent`        | Grid CT1 T Phase Apparent (38836)          | 38836–38837 (32-bit, high word first)    | × 0.1          | VA   | signed | 3-phase only | disabled  |
| `grid_ct_pf`                                 | Grid CT Power Factor                       | 38838–38839 (32-bit, high word first)    | × 0.001        |      | signed |              | disabled  |
| `grid_ct_pf_R`                               | Grid CT Power Factor R                     | 38840–38841 (32-bit, high word first)    | × 0.001        |      | signed |              | disabled  |
| `grid_ct_pf_S`                               | Grid CT Power Factor S                     | 38842–38843 (32-bit, high word first)    | × 0.001        |      | signed | 3-phase only | disabled  |
| `grid_ct_pf_T`                               | Grid CT Power Factor T                     | 38844–38845 (32-bit, high word first)    | × 0.001        |      | signed | 3-phase only | disabled  |
| `reg_38846_grid_ct1_freq`                    | Grid CT1 Freq (38846)                      | 38846–38847 (32-bit, high word first)    | × 0.01         | Hz   | signed |              | disabled  |
| `modbus_protocol_version`                    | Modbus Protocol Version (39000)            | 39000, 39001                             | decoded text   |      |        |              | disabled  |
| `register_39050_raw`                         | Register 39050 raw                         | 39050                                    |                |      |        |              | developer |
| `reg_39051_number_of_strings`                | Number of strings (39051)                  | 39051                                    |                |      |        |              | disabled  |
| `reg_39052_number_of_mppts`                  | Number of MPPTs (39052)                    | 39052                                    |                |      |        |              | disabled  |
| `reg_39053_rated_power_pn`                   | Rated power (Pn) (39053)                   | 39053–39054 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `reg_39055_maximum_active_power_pmax`        | Maximum active power (Pmax) (39055)        | 39055–39056 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `reg_39057_max_apparent_power_smax`          | Max apparent power (Smax) (39057)          | 39057–39058 (32-bit, high word first)    | × 0.001        | kVA  | signed |              | disabled  |
| `reg_39059_max_reactive_power_fed_qmax`      | Max reactive power fed (Qmax) (39059)      | 39059–39060 (32-bit, high word first)    | × 0.001        | kvar | signed |              | disabled  |
| `reg_39061_max_reactive_power_absorbed_qmax` | Max reactive power absorbed (Qmax) (39061) | 39061–39062 (32-bit, high word first)    | × 0.001        | kvar | signed |              | disabled  |
| `inverter_state`                             | Inverter State                             | 39063, 39065, 39066                      | decoded state  |      |        |              | default   |
| `inverter_fault_code`                        | Inverter Fault Code                        | 39067, 39068, 39069 (bitfield)           |                |      |        |              | default   |
| `reg_39067_alarm_1`                          | Alarm 1 (39067)                            | 39067                                    |                |      |        |              | developer |
| `reg_39068_alarm_2`                          | Alarm 2 (39068)                            | 39068                                    |                |      |        |              | developer |
| `reg_39069_alarm_3`                          | Alarm 3 (39069)                            | 39069                                    |                |      |        |              | developer |
| `pv1_voltage`                                | PV1 Voltage                                | 39070                                    | × 0.1          | V    | signed |              | default   |
| `pv1_current`                                | PV1 Current                                | 39071                                    | × 0.01         | A    | signed |              | default   |
| `pv2_voltage`                                | PV2 Voltage                                | 39072                                    | × 0.1          | V    | signed |              | default   |
| `pv2_current`                                | PV2 Current                                | 39073                                    | × 0.01         | A    | signed |              | default   |
| `pv3_voltage`                                | PV3 Voltage                                | 39074                                    | × 0.1          | V    | signed |              | default   |
| `pv3_current`                                | PV3 Current                                | 39075                                    | × 0.01         | A    | signed |              | default   |
| `reg_39118_total_pv_input_power`             | Total PV Input Power (39118)               | 39118–39119 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `grid_voltage_R`                             | Grid Voltage R                             | 39123                                    | × 0.1          | V    | signed |              | disabled  |
| `grid_voltage_S`                             | Grid Voltage S                             | 39124                                    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `grid_voltage_T`                             | Grid Voltage T                             | 39125                                    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `inv_current_R`                              | Inverter Current R                         | 39126–39127 (32-bit, high word first)    | × 0.001        | A    | signed |              | default   |
| `inv_current_S`                              | Inverter Current S                         | 39128–39129 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | default   |
| `inv_current_T`                              | Inverter Current T                         | 39130–39131 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | default   |
| `register_39134_raw`                         | Register 39134 raw                         | 39134–39135 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39136_raw`                         | Register 39136 raw                         | 39136–39137 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39138_raw`                         | Register 39138 raw                         | 39138                                    |                |      |        |              | developer |
| `rfreq`                                      | Grid Frequency                             | 39139                                    | × 0.01         | Hz   | signed |              | disabled  |
| `invtemp`                                    | Inverter Temp                              | 39141                                    | × 0.1          | °C   | signed |              | default   |
| `reg_39142_ambtemp_candidate`                | Ambient Temperature candidate (39142)      | 39142                                    | × 0.1          | °C   | signed |              | developer |
| `reg_39149_cumulative_power_generation`      | Cumulative power generation (39149)        | 39149–39150 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `reg_39151_power_generation_on_the_day`      | Power generation on the day (39151)        | 39151–39152 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `register_39162_raw`                         | Register 39162 raw                         | 39162–39163 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39168_raw`                         | Register 39168 raw                         | 39168–39169 (32-bit, high word first)    |                |      |        |              | developer |
| `eps_rvolt_R`                                | EPS Voltage_R                              | 39201                                    | × 0.1          | V    |        |              | disabled  |
| `eps_rvolt_S`                                | EPS Voltage_S                              | 39202                                    | × 0.1          | V    |        | 3-phase only | disabled  |
| `eps_rvolt_T`                                | EPS Voltage_T                              | 39203                                    | × 0.1          | V    |        | 3-phase only | disabled  |
| `eps_rcurrent_R`                             | EPS Current R                              | 39204–39205 (32-bit, high word first)    | × 0.001        | A    | signed |              | disabled  |
| `eps_rcurrent_S`                             | EPS Current S                              | 39206–39207 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `eps_rcurrent_T`                             | EPS Current T                              | 39208–39209 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `eps_power_R`                                | EPS Power R                                | 39210–39211 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `eps_power_S`                                | EPS Power S                                | 39212–39213 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | disabled  |
| `eps_power_T`                                | EPS Power T                                | 39214–39215 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | disabled  |
| `reg_39216_eps_combined_power`               | EPS Combined Power (39216)                 | 39216–39217 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `eps_frequency`                              | EPS Frequency                              | 39218                                    | × 0.01         | Hz   | signed |              | disabled  |
| `load_power_R`                               | Load Power R                               | 39219–39220 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `reg_39219_load_r_phase_power`               | Load R Phase Power (39219)                 | 39219–39220 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `load_power_S`                               | Load Power S                               | 39221–39222 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `reg_39221_load_s_phase_power`               | Load S Phase Power (39221)                 | 39221–39222 (32-bit, high word first)    |                | W    | signed | 3-phase only | disabled  |
| `load_power_T`                               | Load Power T                               | 39223–39224 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `reg_39223_load_t_phase_power`               | Load T Phase Power (39223)                 | 39223–39224 (32-bit, high word first)    |                | W    | signed | 3-phase only | disabled  |
| `load_power`                                 | Load Power                                 | 39225–39226 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `reg_39225_load_combined_power`              | Load Combined Power (39225)                | 39225–39226 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `batvolt`                                    | Battery Voltage                            | 39227                                    | × 0.1          | V    | signed |              | default   |
| `invbatvolt_1`                               | Inverter Battery 1 Voltage                 | 39227                                    | × 0.1          | V    | signed |              | disabled  |
| `bat_current`                                | Battery Current                            | 39228–39229 (32-bit, high word first)    | × 0.001        | A    | signed |              | default   |
| `invbatcurrent_1`                            | Inverter Battery 1 Current                 | 39228–39229 (32-bit, high word first)    | × 0.001        | A    | signed |              | disabled  |
| `battery_charge_1`                           | Battery 1 Charge                           | 39230–39231 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `battery_discharge_1`                        | Battery 1 Discharge                        | 39230–39231 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `invbatpower_1`                              | Inverter Battery 1 Power                   | 39230–39231 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `battery_charge`                             | Battery Charge                             | 39237–39238 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `battery_discharge`                          | Battery Discharge                          | 39237–39238 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `invbatpower`                                | Inverter Battery Power                     | 39237–39238 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `inv_power_R`                                | Inverter Power R                           | 39248–39249 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `inv_power_S`                                | Inverter Power S                           | 39250–39251 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `inv_power_T`                                | Inverter Power T                           | 39252–39253 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `register_39256_raw`                         | Register 39256 raw                         | 39256–39257 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39258_raw`                         | Register 39258 raw                         | 39258–39259 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39260_raw`                         | Register 39260 raw                         | 39260–39261 (32-bit, high word first)    |                |      |        |              | developer |
| `rpower_S_R`                                 | Inverter Power (Apparent) R                | 39264–39265 (32-bit, high word first)    | × 0.001        | kVA  | signed |              | disabled  |
| `rpower_S_S`                                 | Inverter Power (Apparent) S                | 39266–39267 (32-bit, high word first)    | × 0.001        | kVA  | signed | 3-phase only | disabled  |
| `rpower_S_T`                                 | Inverter Power (Apparent) T                | 39268–39269 (32-bit, high word first)    | × 0.001        | kVA  | signed | 3-phase only | disabled  |
| `reg_39270_combined_apparent`                | Combined Apparent (39270)                  | 39270–39271 (32-bit, high word first)    |                | VA   | signed |              | disabled  |
| `reg_39272_inv_frequency_r`                  | INV Frequency R (39272)                    | 39272                                    | × 0.01         | Hz   | signed |              | disabled  |
| `reg_39273_inv_frequency_s`                  | INV Frequency S (39273)                    | 39273                                    | × 0.01         | Hz   | signed | 3-phase only | disabled  |
| `reg_39274_inv_frequency_t`                  | INV Frequency T (39274)                    | 39274                                    | × 0.01         | Hz   | signed | 3-phase only | disabled  |
| `reg_39275_available_import_power`           | Available Import Power (39275)             | 39275–39276 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_39277_available_export_power`           | Available Export Power (39277)             | 39277–39278 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `pv1_power`                                  | PV1 Power                                  | 39279–39280 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `pv2_power`                                  | PV2 Power                                  | 39281–39282 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `pv3_power`                                  | PV3 Power                                  | 39283–39284 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `reg_39327_mppt1_voltage`                    | MPPT1 Voltage (39327)                      | 39327                                    | × 0.1          | V    | signed |              | disabled  |
| `reg_39328_mppt1_current`                    | MPPT1 Current (39328)                      | 39328                                    | × 0.01         | A    | signed |              | disabled  |
| `reg_39329_mppt1_power`                      | MPPT1 Power (39329)                        | 39329–39330 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_39331_mppt2_voltage`                    | MPPT2 Voltage (39331)                      | 39331                                    | × 0.1          | V    | signed |              | disabled  |
| `reg_39332_mppt2_current`                    | MPPT2 Current (39332)                      | 39332                                    | × 0.01         | A    | signed |              | disabled  |
| `reg_39333_mppt2_power`                      | MPPT2 Power (39333)                        | 39333–39334 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `solar_energy_total`                         | Solar Generation Total                     | 39601–39602 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `solar_energy_today`                         | Solar Generation Today                     | 39603–39604 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `battery_charge_total`                       | Battery Charge Total                       | 39605–39606 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `battery_charge_today`                       | Battery Charge Today                       | 39607–39608 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `battery_discharge_total`                    | Battery Discharge Total                    | 39609–39610 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `battery_discharge_today`                    | Battery Discharge Today                    | 39611–39612 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `feed_in_energy_total`                       | Feed-in Total                              | 39613–39614 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `feed_in_energy_today`                       | Feed-in Today                              | 39615–39616 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `grid_consumption_energy_total`              | Grid Consumption Total                     | 39617–39618 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `grid_consumption_energy_today`              | Grid Consumption Today                     | 39619–39620 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `total_yield_total`                          | Yield Total                                | 39621–39622 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `total_yield_today`                          | Yield Today                                | 39623–39624 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `input_energy_total`                         | Input Energy Total                         | 39625–39626 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `input_energy_today`                         | Input Energy Today                         | 39627–39628 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `load_power_total`                           | Load Energy Total                          | 39629–39630 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `load_energy_today`                          | Load Energy Today                          | 39631–39632 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `register_46001_raw`                         | Register 46001 raw                         | 46001                                    |                |      |        |              | developer |
| `reg_46002_remote_timeout_set`               | Remote Timeout_Set (46002)                 | 46002                                    |                | s    |        |              | disabled  |
| `reg_46003_control_active_power`             | Control Active Power (46003)               | 46003–46004 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_46005_control_reactive_power`           | Control Reactive Power (46005)             | 46005–46006 (32-bit, high word first)    |                | var  | signed |              | disabled  |
| `reg_46007_remote_timeout_countdown`         | Remote Timeout Countdown (46007)           | 46007                                    |                | s    |        |              | disabled  |
| `reg_46018_pwr_limit_bat_up`                 | Pwr_limit Bat_Up (46018)                   | 46018–46019 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_46020_pwr_limit_bat_dn`                 | Pwr_limit Bat_Dn (46020)                   | 46020–46021 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `import_power_limit`                         | Import Power Limit                         | 46501–46502 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_46503_threshold_soc`                    | Threshold SOC (46503)                      | 46503                                    |                | %    |        |              | disabled  |
| `reg_46504_export_peak_limit`                | Export Peak Limit (46504)                  | 46504–46505 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `register_46506_raw`                         | Register 46506 raw                         | 46506                                    |                |      |        |              | developer |
| `register_46507_raw`                         | Register 46507 raw                         | 46507                                    |                |      |        |              | developer |
| `register_46508_raw`                         | Register 46508 raw                         | 46508                                    |                |      |        |              | developer |
| `register_46509_raw`                         | Register 46509 raw                         | 46509                                    |                |      |        |              | developer |
| `register_46510_raw`                         | Register 46510 raw                         | 46510                                    |                |      |        |              | developer |
| `register_46511_raw`                         | Register 46511 raw                         | 46511                                    |                |      |        |              | developer |
| `register_46512_raw`                         | Register 46512 raw                         | 46512                                    |                |      |        |              | developer |
| `register_46513_raw`                         | Register 46513 raw                         | 46513                                    |                |      |        |              | developer |
| `register_46514_raw`                         | Register 46514 raw                         | 46514                                    |                |      |        |              | developer |
| `max_charge_current`                         | Max Charge Current                         | 46607                                    | × 0.1          | A    | signed |              | default   |
| `reg_46607_max_charging_current_setting`     | Max charging current setting (46607)       | 46607                                    | × 0.1          | A    | signed |              | disabled  |
| `max_discharge_current`                      | Max Discharge Current                      | 46608                                    | × 0.1          | A    | signed |              | default   |
| `reg_46608_max_discharge_current_setting`    | Max discharge current setting (46608)      | 46608                                    | × 0.1          | A    | signed |              | disabled  |
| `min_soc`                                    | Min SoC                                    | 46609                                    |                | %    |        |              | default   |
| `reg_46609_minimum_soc`                      | Minimum SoC (46609)                        | 46609                                    |                | %    |        |              | disabled  |
| `max_soc`                                    | Max SoC                                    | 46610                                    |                | %    |        |              | default   |
| `reg_46610_maximum_soc`                      | Maximum SoC (46610)                        | 46610                                    |                | %    |        |              | disabled  |
| `min_soc_on_grid`                            | Min SoC (On Grid)                          | 46611                                    |                | %    |        |              | default   |
| `reg_46611_minimum_soc_ongrid`               | Minimum SoC OnGrid (46611)                 | 46611                                    |                | %    |        |              | disabled  |
| `eps_frequency_select`                       | EPS Frequency (46612)                      | 46612                                    | decoded text   |      |        |              | disabled  |
| `eps_output_mode`                            | EPS Output (46613)                         | 46613                                    | decoded text   |      |        |              | disabled  |
| `register_46614_raw`                         | Register 46614 raw                         | 46614                                    |                |      |        |              | developer |
| `register_46615_raw`                         | Register 46615 raw                         | 46615                                    |                |      |        |              | developer |
| `export_power_limit`                         | Export Power Limit                         | 46616–46617 (32-bit, high word first)    |                | W    | signed |              | default   |
| `reg_46616_export_power_limit`               | Export Power Limit (46616)                 | 46616–46617 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_46618_import_current_limit`             | Import Current Limit (46618)               | 46618                                    | × 0.1          | A    | signed |              | disabled  |
| `reg_46619_export_current_limit`             | Export Current Limit (46619)               | 46619                                    | × 0.1          | A    | signed |              | disabled  |
| `reg_46620_maximum_soc_from_grid`            | Maximum SoC From Grid (46620)              | 46620                                    |                | %    |        |              | disabled  |
| `register_48000_raw`                         | Register 48000 raw                         | 48000                                    |                |      |        |              | developer |
| `register_48010_raw`                         | Register 48010 raw                         | 48010                                    |                |      |        |              | developer |
| `register_48011_raw`                         | Register 48011 raw                         | 48011                                    |                |      |        |              | developer |
| `register_48012_raw`                         | Register 48012 raw                         | 48012                                    |                |      |        |              | developer |
| `register_48013_raw`                         | Register 48013 raw                         | 48013                                    |                |      |        |              | developer |
| `time_group_1_max_soc_from_grid`             | Time Group 1 Max SoC From Grid (48014)     | 48014                                    |                | %    |        |              | disabled  |
| `time_group_1_min_soc_on_grid`               | Time Group 1 Min SoC On Grid (48014)       | 48014                                    |                | %    |        |              | disabled  |
| `reg_48015_time_group_n_fc_fdsoc`            | Time Group (N) FC/FDSOC (48015)            | 48015                                    |                | %    |        |              | disabled  |
| `reg_48016_time_group_n_fc_fdpwr`            | Time Group (N) FC/FDPWR (48016)            | 48016                                    |                | W    |        |              | disabled  |
| `register_49000_raw`                         | Register 49000 raw                         | 49000–49001 (32-bit, high word first)    |                |      |        |              | developer |
| `register_49005_raw`                         | Register 49005 raw                         | 49005                                    |                |      |        |              | developer |
| `register_49006_raw`                         | Register 49006 raw                         | 49006                                    |                |      |        |              | developer |
| `reg_49007_active_power_percentage`          | Active power percentage (49007)            | 49007                                    | × 0.1          | %    | signed |              | disabled  |
| `reg_49008_fixed_active_power_dispatch`      | Fixed active power (dispatch) (49008)      | 49008–49009 (32-bit, high word first)    |                | W    |        |              | disabled  |
| `reg_49010_night_reactive_power`             | Night Reactive power (49010)               | 49010–49011 (32-bit, high word first)    | × 0.001        | kvar | signed |              | disabled  |
| `register_49077_raw`                         | Register 49077 raw                         | 49077                                    |                |      |        |              | developer |
| `register_49078_raw`                         | Register 49078 raw                         | 49078                                    |                |      |        |              | developer |
| `grid_standard`                              | Grid Standard (49079)                      | 49079                                    | decoded text   |      |        |              | disabled  |
| `reg_49136_grid_point_power_limit`           | Grid point power limit (49136)             | 49136–49137 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `register_49206_raw`                         | Register 49206 raw                         | 49206                                    |                |      |        |              | developer |
| `meter1_ct1_type`                            | Meter1 / CT1 Type (49207)                  | 49207                                    | decoded text   |      |        |              | disabled  |
| `register_49209_raw`                         | Register 49209 raw                         | 49209                                    |                |      |        |              | developer |
| `register_49210_raw`                         | Register 49210 raw                         | 49210                                    |                |      |        |              | developer |
| `register_49211_raw`                         | Register 49211 raw                         | 49211                                    |                |      |        |              | developer |
| `register_49212_raw`                         | Register 49212 raw                         | 49212                                    |                |      |        |              | developer |
| `reg_49221_brightness_level`                 | Brightness Level (49221)                   | 49221                                    |                | %    |        |              | disabled  |
| `inverter_date_time`                         | Inverter Date / Time (49222)               | 49222, 49223, 49224, 49225, 49226, 49227 | decoded text   |      |        |              | disabled  |
| `register_49228_raw`                         | Register 49228 raw                         | 49228                                    |                |      |        |              | developer |
| `register_49229_raw`                         | Register 49229 raw                         | 49229                                    |                |      |        |              | developer |
| `reg_49230_idle_loadpower_threshold`         | Idle Loadpower Threshold (49230)           | 49230                                    |                | W    |        |              | disabled  |
| `register_49240_raw`                         | Register 49240 raw                         | 49240                                    |                |      |        |              | developer |
| `register_49241_raw`                         | Register 49241 raw                         | 49241                                    |                |      |        |              | developer |
| `register_49242_raw`                         | Register 49242 raw                         | 49242                                    |                |      |        |              | developer |
| `reg_49243_k1_power_ratio`                   | K1 Power Ratio (49243)                     | 49243                                    |                | %    |        |              | disabled  |
| `reg_49244_k2_power_ratio`                   | K2 Power Ratio (49244)                     | 49244                                    |                | %    |        |              | disabled  |
| `reg_49245_k3_power_ratio`                   | K3 Power Ratio (49245)                     | 49245                                    |                | %    |        |              | disabled  |
| `reg_49246_k4_power_ratio`                   | K4 Power Ratio (49246)                     | 49246                                    |                | %    |        |              | disabled  |
| `register_49247_raw`                         | Register 49247 raw                         | 49247                                    |                |      |        |              | developer |
| `reg_49248_meter_compensation`               | Meter Compensation (49248)                 | 49248                                    |                | W    | signed |              | disabled  |
| `reg_49249_gfci_current`                     | GFCI Current (49249)                       | 49249                                    | × 0.01         | A    | signed |              | disabled  |
