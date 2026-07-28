%% Position controller
KPp = Simulink.Parameter;
KPp.Value = 10.0;
KPp.CoderInfo.StorageClass = 'ExportedGlobal';
KPp.Description = "Position controller proportional gain";
KPp.Unit = "";

%% Current controller P gain
KPi = Simulink.Parameter;
KPi.Value = 8.0;
KPi.CoderInfo.StorageClass = 'ExportedGlobal';
KPi.Description = "Current controller proportional gain";
KPi.Unit = "";

%% Current controller I gain
KIi = Simulink.Parameter;
KIi.Value = 500.0;
KIi.CoderInfo.StorageClass = 'ExportedGlobal';
KIi.Description = "Current controller integral gain";
KIi.Unit = "";

%% Current controller D gain
KDi = Simulink.Parameter;
KDi.Value = 0.001;
KDi.CoderInfo.StorageClass = 'ExportedGlobal';
KDi.Description = "Current controller derivative gain";
KDi.Unit = "";

%% Velocity controller P gain
KPv = Simulink.Parameter;
KPv.Value = 1.0;
KPv.CoderInfo.StorageClass = 'ExportedGlobal';
KPv.Description = "Velocity controller proportional gain";
KPv.Unit = "";

%% Velocity controller I gain
KIv = Simulink.Parameter;
KIv.Value = 20.0;
KIv.CoderInfo.StorageClass = 'ExportedGlobal';
KIv.Description = "Velocity controller integral gain";
KIv.Unit = "";

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
L = Simulink.Parameter;
L.Value = 2e-3;
L.CoderInfo.StorageClass = 'ExportedGlobal';
L.Description = "Motor phase inductance";
L.Unit = "H";

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
R = Simulink.Parameter;
R.Value = 1.2;
R.CoderInfo.StorageClass = 'ExportedGlobal';
R.Description = "Motor phase resistance";
R.Unit = "Ohm";

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

%% Friction
friction = Simulink.Parameter;
friction.Value = true;
friction.CoderInfo.StorageClass = 'ExportedGlobal';
friction.Description = "Friction ON/OFF";
friction.Unit = "";