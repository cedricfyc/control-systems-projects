%% Bandwidths
bandwidth_ratio = 5.0;
W_ci_val = 1000;

W_ci = Simulink.Parameter;
W_ci.Value = W_ci_val;   
W_ci.CoderInfo.StorageClass = 'ExportedGlobal';
W_ci.Description = "Inverter first-order time constant";
W_ci.Unit = "1/s";

W_cw = Simulink.Parameter;
W_cw.Value = W_ci_val/bandwidth_ratio;        
W_cw.CoderInfo.StorageClass = 'ExportedGlobal';
W_cw.Description = "Inverter first-order time constant";
W_cw.Unit = "1/s";

W_cq = Simulink.Parameter;
W_cq.Value = W_ci_val/bandwidth_ratio/bandwidth_ratio;
W_cq.CoderInfo.StorageClass = 'ExportedGlobal';
W_cq.Description = "Inverter first-order time constant";
W_cq.Unit = "1/s";

%% Inverter time constant
t_inv = Simulink.Parameter;
t_inv.Value = 200e-6;          % 200 µs
t_inv.CoderInfo.StorageClass = 'ExportedGlobal';
t_inv.Description = "Inverter first-order time constant";
t_inv.Unit = "s";

%% DC bus voltage
U_DC = Simulink.Parameter;
U_DC.Value = 48.0;
U_DC.CoderInfo.StorageClass = 'ExportedGlobal';
U_DC.Description = "DC supply voltage";
U_DC.Unit = "V";

%% Motor inductance
L_a = Simulink.Parameter;
L_a.Value = 2e-3;
L_a.CoderInfo.StorageClass = 'ExportedGlobal';
L_a.Description = "Motor phase inductance";
L_a.Unit = "H";

%% Torque constant
k_t = Simulink.Parameter;
k_t.Value = 0.1;
k_t.CoderInfo.StorageClass = 'ExportedGlobal';
k_t.Description = "Motor torque constant";
k_t.Unit = "N*m/A";

%% Back EMF constant
k_e = Simulink.Parameter;
k_e.Value = 0.1;
k_e.CoderInfo.StorageClass = 'ExportedGlobal';
k_e.Description = "Back EMF constant";
k_e.Unit = "V/(rad/s)";

%% Motor resistance
R_a = Simulink.Parameter;
R_a.Value = 1.2;
R_a.CoderInfo.StorageClass = 'ExportedGlobal';
R_a.Description = "Motor phase resistance";
R_a.Unit = "Ohm";

%% Motor inertia
J_motor = Simulink.Parameter;
J_motor.Value = 5e-4;
J_motor.CoderInfo.StorageClass = 'ExportedGlobal';
J_motor.Description = "Motor inertia";
J_motor.Unit = "kg*m^2";

%% Load inertia
J_load = Simulink.Parameter;
J_load.Value = 1e-3;
J_load.CoderInfo.StorageClass = 'ExportedGlobal';
J_load.Description = "Load inertia";
J_load.Unit = "kg*m^2";

%% Coulomb friction
kFrc = Simulink.Parameter;
kFrc.Value = 0.02;
kFrc.CoderInfo.StorageClass = 'ExportedGlobal';
kFrc.Description = "Coulomb friction coefficient";
kFrc.Unit = "N*m";

%% Sliding (viscous) friction
kFrs = Simulink.Parameter;
kFrs.Value = 0.001;
kFrs.CoderInfo.StorageClass = 'ExportedGlobal';
kFrs.Description = "Viscous friction coefficient";
kFrs.Unit = "N*m/(rad/s)";

%% Choice of mechanics
choice = Simulink.Parameter;
choice.Value = 1;
choice.CoderInfo.StorageClass = 'ExportedGlobal';
choice.Description = "Choice of variant subsystem";
choice.Unit = "";