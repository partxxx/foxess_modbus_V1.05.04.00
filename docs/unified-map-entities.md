# Unified map (EXPERIMENTAL): entity reference

Generated from the integration code (`Inv.UNIFIED_3PH` / `Inv.UNIFIED_1PH`). Addresses are holding registers.

_Enabled_: `default` = enabled when created, `disabled` = created disabled (enable it in HA to test it),
`developer` = only created with the _Create raw register entities_ option, and disabled.

Three-phase models: 234 entities; single-phase models: 200 (the rows marked _3-phase only_ are left out).

| Key                                          | Name                                    | Register(s)                              | Scale          | Unit | Signed | Phases       | Enabled   |
| -------------------------------------------- | --------------------------------------- | ---------------------------------------- | -------------- | ---- | ------ | ------------ | --------- |
| `pv1_energy_total`                           | PV1 Energy Total                        | integrated from `pv1_power`              |                | kWh  |        |              | default   |
| `pv2_energy_total`                           | PV2 Energy Total                        | integrated from `pv2_power`              |                | kWh  |        |              | default   |
| `pv3_energy_total`                           | PV3 Energy Total                        | integrated from `pv3_power`              |                | kWh  |        |              | default   |
| `master_version`                             | Inverter Master Version                 | 36001                                    | decimal digits |      |        |              | default   |
| `slave_version`                              | Inverter Slave Version                  | 36002                                    | decimal digits |      |        |              | default   |
| `manager_version`                            | Inverter Manager Version                | 36003                                    | hex digits     |      |        |              | default   |
| `bms1_master_version`                        | BMS1 BAT Master Version                 | 37003                                    | decoded text   |      |        |              | disabled  |
| `register_37004_raw`                         | Register 37004 Raw                      | 37004                                    |                |      |        |              | developer |
| `register_37032_raw`                         | Register 37032 Raw                      | 37032                                    |                |      |        |              | developer |
| `register_37033_raw`                         | Register 37033 Raw                      | 37033                                    |                |      |        |              | developer |
| `register_37034_raw`                         | Register 37034 Raw                      | 37034                                    |                |      |        |              | developer |
| `batvolt_1`                                  | BMS1 BAT Voltage                        | 37609                                    | × 0.1          | V    |        |              | disabled  |
| `bat_current_1`                              | BMS1 BAT Current                        | 37610                                    | × 0.1          | A    | signed |              | disabled  |
| `battery_temp`                               | BMS1 BAT Temperature                    | 37611                                    | × 0.1          | °C   | signed |              | default   |
| `battery_soc`                                | BMS1 BAT SoC                            | 37612                                    |                | %    |        |              | default   |
| `reg_37615_bms_max_current_candidate`        | BMS1 BAT Current Max Candidate          | 37615                                    | × 0.1          | A    |        |              | developer |
| `bms_cell_temp_high`                         | BMS1 BAT Cell Temperature Max           | 37617                                    | × 0.1          | °C   | signed |              | default   |
| `bms_cell_temp_low`                          | BMS1 BAT Cell Temperature Min           | 37618                                    | × 0.1          | °C   | signed |              | default   |
| `bms_cell_mv_high`                           | BMS1 BAT Cell Voltage Max               | 37619                                    |                | mV   |        |              | default   |
| `bms_cell_mv_low`                            | BMS1 BAT Cell Voltage Min               | 37620                                    |                | mV   |        |              | default   |
| `battery_soh`                                | BMS1 BAT SoH                            | 37624                                    |                | %    |        |              | default   |
| `reg_37626_bms1_fault1`                      | BMS1 BAT Fault1 Raw                     | 37626                                    |                |      |        |              | developer |
| `reg_37627_bms1_fault2`                      | BMS1 BAT Fault2 Raw                     | 37627                                    |                |      |        |              | developer |
| `reg_37628_bms1_fault3`                      | BMS1 BAT Fault3 Raw                     | 37628                                    |                |      |        |              | developer |
| `reg_37629_bms1_fault4`                      | BMS1 BAT Fault4 Raw                     | 37629                                    |                |      |        |              | developer |
| `reg_37630_bms1_fault5`                      | BMS1 BAT Fault5 Raw                     | 37630                                    |                |      |        |              | developer |
| `reg_37631_bms1_fault6`                      | BMS1 BAT Fault6 Raw                     | 37631                                    |                |      |        |              | developer |
| `bms_kwh_remaining`                          | BMS1 BAT Energy Remaining               | 37632                                    | × 0.01         | kWh  |        |              | default   |
| `reg_37633_bms1_fcc_capacity`                | BMS1 BAT Capacity Full Charge           | 37633                                    | × 0.1          | Ah   |        |              | disabled  |
| `reg_37635_bms1_design_energy`               | BMS1 BAT Energy Nominal                 | 37635                                    | × 10           | Wh   |        |              | disabled  |
| `register_37636_raw`                         | Register 37636 Raw                      | 37636                                    |                |      |        |              | developer |
| `register_38801_raw`                         | Register 38801 Raw                      | 38801                                    |                |      |        |              | developer |
| `reg_38802_grid_ct1_r_phase_voltage`         | Meter CT1 R Voltage                     | 38802–38803 (32-bit, high word first)    | × 0.1          | V    | signed |              | disabled  |
| `reg_38804_grid_ct1_s_phase_voltage`         | Meter CT1 S Voltage                     | 38804–38805 (32-bit, high word first)    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `reg_38806_grid_ct1_t_phase_voltage`         | Meter CT1 T Voltage                     | 38806–38807 (32-bit, high word first)    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `reg_38808_grid_ct1_r_phase_current`         | Meter CT1 R Current                     | 38808–38809 (32-bit, high word first)    | × 0.001        | A    | signed |              | disabled  |
| `reg_38810_grid_ct1_s_phase_current`         | Meter CT1 S Current                     | 38810–38811 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `reg_38812_grid_ct1_t_phase_current`         | Meter CT1 T Current                     | 38812–38813 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `feed_in`                                    | Grid Power Export                       | 38814–38815 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | disabled  |
| `grid_consumption`                           | Grid Power Import                       | 38814–38815 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | disabled  |
| `grid_ct`                                    | Meter CT1 Power                         | 38814–38815 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | disabled  |
| `feed_in_R`                                  | Grid R Power Export                     | 38816–38817 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | default   |
| `grid_consumption_R`                         | Grid R Power Import                     | 38816–38817 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | default   |
| `grid_ct_R`                                  | Meter CT1 R Power                       | 38816–38817 (32-bit, high word first)    | × 0.0001       | kW   | signed |              | default   |
| `feed_in_S`                                  | Grid S Power Export                     | 38818–38819 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_consumption_S`                         | Grid S Power Import                     | 38818–38819 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_ct_S`                                  | Meter CT1 S Power                       | 38818–38819 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `feed_in_T`                                  | Grid T Power Export                     | 38820–38821 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_consumption_T`                         | Grid T Power Import                     | 38820–38821 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `grid_ct_T`                                  | Meter CT1 T Power                       | 38820–38821 (32-bit, high word first)    | × 0.0001       | kW   | signed | 3-phase only | default   |
| `reg_38822_grid_ct1_combined_reactive`       | Meter CT1 Reactive Power                | 38822–38823 (32-bit, high word first)    | × 0.1          | var  | signed |              | disabled  |
| `reg_38824_grid_ct1_r_phase_reactive`        | Meter CT1 R Reactive Power              | 38824–38825 (32-bit, high word first)    | × 0.1          | var  | signed |              | disabled  |
| `reg_38826_grid_ct1_s_phase_reactive`        | Meter CT1 S Reactive Power              | 38826–38827 (32-bit, high word first)    | × 0.1          | var  | signed | 3-phase only | disabled  |
| `reg_38828_grid_ct1_t_phase_reactive`        | Meter CT1 T Reactive Power              | 38828–38829 (32-bit, high word first)    | × 0.1          | var  | signed | 3-phase only | disabled  |
| `reg_38830_grid_ct1_combined_apparent`       | Meter CT1 Apparent Power                | 38830–38831 (32-bit, high word first)    | × 0.1          | VA   | signed |              | disabled  |
| `reg_38832_grid_ct1_r_phase_apparent`        | Meter CT1 R Apparent Power              | 38832–38833 (32-bit, high word first)    | × 0.1          | VA   | signed |              | disabled  |
| `reg_38834_grid_ct1_s_phase_apparent`        | Meter CT1 S Apparent Power              | 38834–38835 (32-bit, high word first)    | × 0.1          | VA   | signed | 3-phase only | disabled  |
| `reg_38836_grid_ct1_t_phase_apparent`        | Meter CT1 T Apparent Power              | 38836–38837 (32-bit, high word first)    | × 0.1          | VA   | signed | 3-phase only | disabled  |
| `grid_ct_pf`                                 | Meter CT1 Power Factor                  | 38838–38839 (32-bit, high word first)    | × 0.001        |      | signed |              | disabled  |
| `grid_ct_pf_R`                               | Meter CT1 R Power Factor                | 38840–38841 (32-bit, high word first)    | × 0.001        |      | signed |              | disabled  |
| `grid_ct_pf_S`                               | Meter CT1 S Power Factor                | 38842–38843 (32-bit, high word first)    | × 0.001        |      | signed | 3-phase only | disabled  |
| `grid_ct_pf_T`                               | Meter CT1 T Power Factor                | 38844–38845 (32-bit, high word first)    | × 0.001        |      | signed | 3-phase only | disabled  |
| `reg_38846_grid_ct1_freq`                    | Meter CT1 Frequency                     | 38846–38847 (32-bit, high word first)    | × 0.01         | Hz   | signed |              | disabled  |
| `modbus_protocol_version`                    | Modbus Protocol Version                 | 39000, 39001                             | decoded text   |      |        |              | disabled  |
| `register_39050_raw`                         | Register 39050 Raw                      | 39050                                    |                |      |        |              | developer |
| `reg_39051_number_of_strings`                | PV String Count                         | 39051                                    |                |      |        |              | disabled  |
| `reg_39052_number_of_mppts`                  | MPPT Count                              | 39052                                    |                |      |        |              | disabled  |
| `reg_39053_rated_power_pn`                   | Inverter Power Rated                    | 39053–39054 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `reg_39055_maximum_active_power_pmax`        | Inverter Active Power Max               | 39055–39056 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `reg_39057_max_apparent_power_smax`          | Inverter Apparent Power Max             | 39057–39058 (32-bit, high word first)    | × 0.001        | kVA  | signed |              | disabled  |
| `reg_39059_max_reactive_power_fed_qmax`      | Inverter Reactive Power Export Max      | 39059–39060 (32-bit, high word first)    | × 0.001        | kvar | signed |              | disabled  |
| `reg_39061_max_reactive_power_absorbed_qmax` | Inverter Reactive Power Import Max      | 39061–39062 (32-bit, high word first)    | × 0.001        | kvar | signed |              | disabled  |
| `inverter_state`                             | Inverter State                          | 39063, 39065, 39066                      | decoded state  |      |        |              | default   |
| `inverter_fault_code`                        | Inverter Fault Code                     | 39067, 39068, 39069 (bitfield)           |                |      |        |              | default   |
| `reg_39067_alarm_1`                          | Inverter Alarm1 Raw                     | 39067                                    |                |      |        |              | developer |
| `reg_39068_alarm_2`                          | Inverter Alarm2 Raw                     | 39068                                    |                |      |        |              | developer |
| `reg_39069_alarm_3`                          | Inverter Alarm3 Raw                     | 39069                                    |                |      |        |              | developer |
| `pv1_voltage`                                | PV1 Voltage                             | 39070                                    | × 0.1          | V    | signed |              | default   |
| `pv1_current`                                | PV1 Current                             | 39071                                    | × 0.01         | A    | signed |              | default   |
| `pv2_voltage`                                | PV2 Voltage                             | 39072                                    | × 0.1          | V    | signed |              | default   |
| `pv2_current`                                | PV2 Current                             | 39073                                    | × 0.01         | A    | signed |              | default   |
| `pv3_voltage`                                | PV3 Voltage                             | 39074                                    | × 0.1          | V    | signed |              | default   |
| `pv3_current`                                | PV3 Current                             | 39075                                    | × 0.01         | A    | signed |              | default   |
| `pv_power_now`                               | PV Power                                | 39118–39119 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `grid_voltage_R`                             | Grid R Voltage                          | 39123                                    | × 0.1          | V    | signed |              | disabled  |
| `grid_voltage_S`                             | Grid S Voltage                          | 39124                                    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `grid_voltage_T`                             | Grid T Voltage                          | 39125                                    | × 0.1          | V    | signed | 3-phase only | disabled  |
| `inv_current_R`                              | Inverter R Current                      | 39126–39127 (32-bit, high word first)    | × 0.001        | A    | signed |              | default   |
| `inv_current_S`                              | Inverter S Current                      | 39128–39129 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | default   |
| `inv_current_T`                              | Inverter T Current                      | 39130–39131 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | default   |
| `register_39134_raw`                         | Register 39134 Raw                      | 39134–39135 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39136_raw`                         | Register 39136 Raw                      | 39136–39137 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39138_raw`                         | Register 39138 Raw                      | 39138                                    |                |      |        |              | developer |
| `rfreq`                                      | Grid Frequency                          | 39139                                    | × 0.01         | Hz   | signed |              | disabled  |
| `invtemp`                                    | Inverter Temperature                    | 39141                                    | × 0.1          | °C   | signed |              | default   |
| `reg_39142_ambtemp_candidate`                | Inverter Ambient Temperature Candidate  | 39142                                    | × 0.1          | °C   | signed |              | developer |
| `reg_39149_cumulative_power_generation`      | Inverter Energy Generation Total        | 39149–39150 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `reg_39151_power_generation_on_the_day`      | Inverter Energy Generation Today        | 39151–39152 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `register_39162_raw`                         | Register 39162 Raw                      | 39162–39163 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39168_raw`                         | Register 39168 Raw                      | 39168–39169 (32-bit, high word first)    |                |      |        |              | developer |
| `eps_rvolt_R`                                | EPS R Voltage                           | 39201                                    | × 0.1          | V    |        |              | disabled  |
| `eps_rvolt_S`                                | EPS S Voltage                           | 39202                                    | × 0.1          | V    |        | 3-phase only | disabled  |
| `eps_rvolt_T`                                | EPS T Voltage                           | 39203                                    | × 0.1          | V    |        | 3-phase only | disabled  |
| `eps_rcurrent_R`                             | EPS R Current                           | 39204–39205 (32-bit, high word first)    | × 0.001        | A    | signed |              | disabled  |
| `eps_rcurrent_S`                             | EPS S Current                           | 39206–39207 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `eps_rcurrent_T`                             | EPS T Current                           | 39208–39209 (32-bit, high word first)    | × 0.001        | A    | signed | 3-phase only | disabled  |
| `eps_power_R`                                | EPS R Power                             | 39210–39211 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `eps_power_S`                                | EPS S Power                             | 39212–39213 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | disabled  |
| `eps_power_T`                                | EPS T Power                             | 39214–39215 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | disabled  |
| `reg_39216_eps_combined_power`               | EPS Power                               | 39216–39217 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `eps_frequency`                              | EPS Frequency                           | 39218                                    | × 0.01         | Hz   | signed |              | disabled  |
| `load_power_R`                               | Load R Power                            | 39219–39220 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `load_power_S`                               | Load S Power                            | 39221–39222 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `load_power_T`                               | Load T Power                            | 39223–39224 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `load_power`                                 | Load Power                              | 39225–39226 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `batvolt`                                    | Inverter BAT1 Voltage                   | 39227                                    | × 0.1          | V    | signed |              | default   |
| `bat_current`                                | Inverter BAT1 Current                   | 39228–39229 (32-bit, high word first)    | × 0.001        | A    | signed |              | default   |
| `battery_charge_1`                           | Inverter BAT1 Power Charge              | 39230–39231 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `battery_discharge_1`                        | Inverter BAT1 Power Discharge           | 39230–39231 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `invbatpower_1`                              | Inverter BAT1 Power                     | 39230–39231 (32-bit, high word first)    | × 0.001        | kW   | signed |              | disabled  |
| `battery_charge`                             | Inverter BAT Power Charge               | 39237–39238 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `battery_discharge`                          | Inverter BAT Power Discharge            | 39237–39238 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `invbatpower`                                | Inverter BAT Power                      | 39237–39238 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `inv_power_R`                                | Inverter R Power                        | 39248–39249 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `inv_power_S`                                | Inverter S Power                        | 39250–39251 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `inv_power_T`                                | Inverter T Power                        | 39252–39253 (32-bit, high word first)    | × 0.001        | kW   | signed | 3-phase only | default   |
| `register_39256_raw`                         | Register 39256 Raw                      | 39256–39257 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39258_raw`                         | Register 39258 Raw                      | 39258–39259 (32-bit, high word first)    |                |      |        |              | developer |
| `register_39260_raw`                         | Register 39260 Raw                      | 39260–39261 (32-bit, high word first)    |                |      |        |              | developer |
| `rpower_S_R`                                 | Inverter R Apparent Power               | 39264–39265 (32-bit, high word first)    | × 0.001        | kVA  | signed |              | disabled  |
| `rpower_S_S`                                 | Inverter S Apparent Power               | 39266–39267 (32-bit, high word first)    | × 0.001        | kVA  | signed | 3-phase only | disabled  |
| `rpower_S_T`                                 | Inverter T Apparent Power               | 39268–39269 (32-bit, high word first)    | × 0.001        | kVA  | signed | 3-phase only | disabled  |
| `reg_39270_combined_apparent`                | Inverter Apparent Power                 | 39270–39271 (32-bit, high word first)    |                | VA   | signed |              | disabled  |
| `reg_39272_inv_frequency_r`                  | Inverter R Frequency                    | 39272                                    | × 0.01         | Hz   | signed |              | disabled  |
| `reg_39273_inv_frequency_s`                  | Inverter S Frequency                    | 39273                                    | × 0.01         | Hz   | signed | 3-phase only | disabled  |
| `reg_39274_inv_frequency_t`                  | Inverter T Frequency                    | 39274                                    | × 0.01         | Hz   | signed | 3-phase only | disabled  |
| `reg_39275_available_import_power`           | Inverter Power Import Available         | 39275–39276 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_39277_available_export_power`           | Inverter Power Export Available         | 39277–39278 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `pv1_power`                                  | PV1 Power                               | 39279–39280 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `pv2_power`                                  | PV2 Power                               | 39281–39282 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `pv3_power`                                  | PV3 Power                               | 39283–39284 (32-bit, high word first)    | × 0.001        | kW   | signed |              | default   |
| `reg_39327_mppt1_voltage`                    | MPPT1 Voltage                           | 39327                                    | × 0.1          | V    | signed |              | disabled  |
| `reg_39328_mppt1_current`                    | MPPT1 Current                           | 39328                                    | × 0.01         | A    | signed |              | disabled  |
| `reg_39329_mppt1_power`                      | MPPT1 Power                             | 39329–39330 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_39331_mppt2_voltage`                    | MPPT2 Voltage                           | 39331                                    | × 0.1          | V    | signed |              | disabled  |
| `reg_39332_mppt2_current`                    | MPPT2 Current                           | 39332                                    | × 0.01         | A    | signed |              | disabled  |
| `reg_39333_mppt2_power`                      | MPPT2 Power                             | 39333–39334 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `solar_energy_total`                         | PV Energy Total                         | 39601–39602 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `solar_energy_today`                         | PV Energy Today                         | 39603–39604 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `battery_charge_total`                       | Inverter BAT Energy Charge Total        | 39605–39606 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `battery_charge_today`                       | Inverter BAT Energy Charge Today        | 39607–39608 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `battery_discharge_total`                    | Inverter BAT Energy Discharge Total     | 39609–39610 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `battery_discharge_today`                    | Inverter BAT Energy Discharge Today     | 39611–39612 (32-bit, high word first)    | × 0.01         | kWh  |        |              | disabled  |
| `feed_in_energy_total`                       | Grid Energy Export Total                | 39613–39614 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `feed_in_energy_today`                       | Grid Energy Export Today                | 39615–39616 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `grid_consumption_energy_total`              | Grid Energy Import Total                | 39617–39618 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `grid_consumption_energy_today`              | Grid Energy Import Today                | 39619–39620 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `total_yield_total`                          | Inverter Yield Energy Total             | 39621–39622 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `total_yield_today`                          | Inverter Yield Energy Today             | 39623–39624 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `input_energy_total`                         | Inverter Input Energy Total             | 39625–39626 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `input_energy_today`                         | Inverter Input Energy Today             | 39627–39628 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `load_power_total`                           | Load Energy Total                       | 39629–39630 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `load_energy_today`                          | Load Energy Today                       | 39631–39632 (32-bit, high word first)    | × 0.01         | kWh  |        |              | default   |
| `register_46001_raw`                         | Register 46001 Raw                      | 46001                                    |                |      |        |              | developer |
| `reg_46002_remote_timeout_set`               | Inverter Remote Control Timeout         | 46002                                    |                | s    |        |              | disabled  |
| `reg_46003_control_active_power`             | Inverter Active Power Setpoint          | 46003–46004 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_46005_control_reactive_power`           | Inverter Reactive Power Setpoint        | 46005–46006 (32-bit, high word first)    |                | var  | signed |              | disabled  |
| `reg_46007_remote_timeout_countdown`         | Inverter Remote Control Countdown       | 46007                                    |                | s    |        |              | disabled  |
| `reg_46018_pwr_limit_bat_up`                 | Inverter BAT Power Discharge Available  | 46018–46019 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_46020_pwr_limit_bat_dn`                 | Inverter BAT Power Charge Available     | 46020–46021 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `import_power_limit`                         | Inverter Power Import Limit             | 46501–46502 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `reg_46503_threshold_soc`                    | Inverter BAT SoC Threshold              | 46503                                    |                | %    |        |              | disabled  |
| `reg_46504_export_peak_limit`                | Inverter Power Export Peak Limit        | 46504–46505 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `register_46506_raw`                         | Register 46506 Raw                      | 46506                                    |                |      |        |              | developer |
| `register_46507_raw`                         | Register 46507 Raw                      | 46507                                    |                |      |        |              | developer |
| `register_46508_raw`                         | Register 46508 Raw                      | 46508                                    |                |      |        |              | developer |
| `register_46509_raw`                         | Register 46509 Raw                      | 46509                                    |                |      |        |              | developer |
| `register_46510_raw`                         | Register 46510 Raw                      | 46510                                    |                |      |        |              | developer |
| `register_46511_raw`                         | Register 46511 Raw                      | 46511                                    |                |      |        |              | developer |
| `register_46512_raw`                         | Register 46512 Raw                      | 46512                                    |                |      |        |              | developer |
| `register_46513_raw`                         | Register 46513 Raw                      | 46513                                    |                |      |        |              | developer |
| `register_46514_raw`                         | Register 46514 Raw                      | 46514                                    |                |      |        |              | developer |
| `max_charge_current`                         | Inverter BAT Current Charge Max         | 46607                                    | × 0.1          | A    | signed |              | default   |
| `max_discharge_current`                      | Inverter BAT Current Discharge Max      | 46608                                    | × 0.1          | A    | signed |              | default   |
| `min_soc`                                    | Inverter BAT SoC Min                    | 46609                                    |                | %    |        |              | default   |
| `max_soc`                                    | Inverter BAT SoC Max                    | 46610                                    |                | %    |        |              | default   |
| `min_soc_on_grid`                            | Inverter BAT SoC Min On Grid            | 46611                                    |                | %    |        |              | default   |
| `eps_frequency_select`                       | EPS Frequency Setting                   | 46612                                    | decoded text   |      |        |              | disabled  |
| `eps_output_mode`                            | EPS Output Mode                         | 46613                                    | decoded text   |      |        |              | disabled  |
| `register_46615_raw`                         | Register 46615 Raw                      | 46615                                    |                |      |        |              | developer |
| `export_power_limit`                         | Inverter Power Export Limit             | 46616–46617 (32-bit, high word first)    |                | W    | signed |              | default   |
| `reg_46618_import_current_limit`             | Inverter Current Import Limit           | 46618                                    | × 0.1          | A    | signed |              | disabled  |
| `reg_46619_export_current_limit`             | Inverter Current Export Limit           | 46619                                    | × 0.1          | A    | signed |              | disabled  |
| `reg_46620_maximum_soc_from_grid`            | Inverter BAT SoC Max From Grid          | 46620                                    |                | %    |        |              | disabled  |
| `register_48000_raw`                         | Register 48000 Raw                      | 48000                                    |                |      |        |              | developer |
| `register_48010_raw`                         | Register 48010 Raw                      | 48010                                    |                |      |        |              | developer |
| `register_48011_raw`                         | Register 48011 Raw                      | 48011                                    |                |      |        |              | developer |
| `register_48012_raw`                         | Register 48012 Raw                      | 48012                                    |                |      |        |              | developer |
| `register_48013_raw`                         | Register 48013 Raw                      | 48013                                    |                |      |        |              | developer |
| `time_group_1_max_soc_from_grid`             | Time Group1 SoC Max From Grid           | 48014                                    |                | %    |        |              | disabled  |
| `time_group_1_min_soc_on_grid`               | Time Group1 SoC Min On Grid             | 48014                                    |                | %    |        |              | disabled  |
| `reg_48015_time_group_n_fc_fdsoc`            | Time Group1 FC/FD SoC Candidate         | 48015                                    |                | %    |        |              | disabled  |
| `reg_48016_time_group_n_fc_fdpwr`            | Time Group1 FC/FD Power Candidate       | 48016                                    |                | W    |        |              | disabled  |
| `register_49000_raw`                         | Register 49000 Raw                      | 49000–49001 (32-bit, high word first)    |                |      |        |              | developer |
| `register_49005_raw`                         | Register 49005 Raw                      | 49005                                    |                |      |        |              | developer |
| `register_49006_raw`                         | Register 49006 Raw                      | 49006                                    |                |      |        |              | developer |
| `reg_49007_active_power_percentage`          | Inverter Active Power Percentage        | 49007                                    | × 0.1          | %    | signed |              | disabled  |
| `reg_49008_fixed_active_power_dispatch`      | Inverter Active Power Dispatch Setpoint | 49008–49009 (32-bit, high word first)    |                | W    |        |              | disabled  |
| `reg_49010_night_reactive_power`             | Inverter Reactive Power Night           | 49010–49011 (32-bit, high word first)    | × 0.001        | kvar | signed |              | disabled  |
| `register_49077_raw`                         | Register 49077 Raw                      | 49077                                    |                |      |        |              | developer |
| `register_49078_raw`                         | Register 49078 Raw                      | 49078                                    |                |      |        |              | developer |
| `grid_standard`                              | Grid Standard                           | 49079                                    | decoded text   |      |        |              | disabled  |
| `reg_49136_grid_point_power_limit`           | Grid Connection Power Limit             | 49136–49137 (32-bit, high word first)    |                | W    | signed |              | disabled  |
| `register_49206_raw`                         | Register 49206 Raw                      | 49206                                    |                |      |        |              | developer |
| `meter1_ct1_type`                            | Meter1/CT1 Type                         | 49207                                    | decoded text   |      |        |              | disabled  |
| `register_49209_raw`                         | Register 49209 Raw                      | 49209                                    |                |      |        |              | developer |
| `register_49210_raw`                         | Register 49210 Raw                      | 49210                                    |                |      |        |              | developer |
| `register_49211_raw`                         | Register 49211 Raw                      | 49211                                    |                |      |        |              | developer |
| `register_49212_raw`                         | Register 49212 Raw                      | 49212                                    |                |      |        |              | developer |
| `reg_49221_brightness_level`                 | Inverter Display Brightness             | 49221                                    |                | %    |        |              | disabled  |
| `inverter_date_time`                         | Inverter Date Time                      | 49222, 49223, 49224, 49225, 49226, 49227 | decoded text   |      |        |              | disabled  |
| `register_49228_raw`                         | Register 49228 Raw                      | 49228                                    |                |      |        |              | developer |
| `register_49229_raw`                         | Register 49229 Raw                      | 49229                                    |                |      |        |              | developer |
| `reg_49230_idle_loadpower_threshold`         | Load Power Idle Threshold               | 49230                                    |                | W    |        |              | disabled  |
| `register_49240_raw`                         | Register 49240 Raw                      | 49240                                    |                |      |        |              | developer |
| `register_49241_raw`                         | Register 49241 Raw                      | 49241                                    |                |      |        |              | developer |
| `register_49242_raw`                         | Register 49242 Raw                      | 49242                                    |                |      |        |              | developer |
| `reg_49243_k1_power_ratio`                   | K1 Power Ratio                          | 49243                                    |                | %    |        |              | disabled  |
| `reg_49244_k2_power_ratio`                   | K2 Power Ratio                          | 49244                                    |                | %    |        |              | disabled  |
| `reg_49245_k3_power_ratio`                   | K3 Power Ratio                          | 49245                                    |                | %    |        |              | disabled  |
| `reg_49246_k4_power_ratio`                   | K4 Power Ratio                          | 49246                                    |                | %    |        |              | disabled  |
| `register_49247_raw`                         | Register 49247 Raw                      | 49247                                    |                |      |        |              | developer |
| `reg_49248_meter_compensation`               | Meter Power Compensation                | 49248                                    |                | W    | signed |              | disabled  |
| `reg_49249_gfci_current`                     | Inverter GFCI Current                   | 49249                                    | × 0.01         | A    | signed |              | disabled  |
