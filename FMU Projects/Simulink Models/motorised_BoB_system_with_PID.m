%% Bandwidths
bandwidth_ratio = 5.0;
W_ci_val = 1000;

W_ci = Simulink.Parameter;
W_ci.Value = W_ci_val;   
W_ci.CoderInfo.StorageClass = 'ExportedGlobal';
W_ci.Description = "Current loop bandwidth";
W_ci.Unit = "1/s";

W_cw = Simulink.Parameter;
W_cw.Value = W_ci_val/bandwidth_ratio;        
W_cw.CoderInfo.StorageClass = 'ExportedGlobal';
W_cw.Description = "Velocity loop bandwidth";
W_cw.Unit = "1/s";

W_cq = Simulink.Parameter;
W_cq.Value = W_ci_val/bandwidth_ratio/bandwidth_ratio;
W_cq.CoderInfo.StorageClass = 'ExportedGlobal';
W_cq.Description = "Position loop bandwidth";
W_cq.Unit = "1/s";

%% Inverter time constant
t_inv = Simulink.Parameter;
t_inv.Value = 200e-6;          % 200 µs
t_inv.CoderInfo.StorageClass = 'ExportedGlobal';
t_inv.Description = "Inverter first-order time constant";
t_inv.Unit = "s";

%% DC bus voltage
U_DC = Simulink.Parameter;
U_DC.Value = 240.0;
U_DC.CoderInfo.StorageClass = 'ExportedGlobal';
U_DC.Description = "DC supply voltage";
U_DC.Unit = "V";

%% Motor inductance
L_a = Simulink.Parameter;
L_a.Value = 1.5e-3;
L_a.CoderInfo.StorageClass = 'ExportedGlobal';
L_a.Description = "Motor phase inductance";
L_a.Unit = "H";

%% Torque constant
k_t = Simulink.Parameter;
k_t.Value = 0.8;
k_t.CoderInfo.StorageClass = 'ExportedGlobal';
k_t.Description = "Motor torque constant";
k_t.Unit = "N*m/A";

%% Back EMF constant
k_e = Simulink.Parameter;
k_e.Value = 0.8;
k_e.CoderInfo.StorageClass = 'ExportedGlobal';
k_e.Description = "Back EMF constant";
k_e.Unit = "V/(rad/s)";

%% Motor resistance
R_a = Simulink.Parameter;
R_a.Value = 0.15;
R_a.CoderInfo.StorageClass = 'ExportedGlobal';
R_a.Description = "Motor phase resistance";
R_a.Unit = "Ohm";

%% Motor inertia
J_motor = Simulink.Parameter;
J_motor.Value = 2e-2;
J_motor.CoderInfo.StorageClass = 'ExportedGlobal';
J_motor.Description = "Motor inertia";
J_motor.Unit = "kg*m^2";

%% PID Controller
% Classical PID 

K_u = 10.0;
T_u = 0.7428;

KPpid = Simulink.Parameter;
KPpid.Value = 0.6*K_u;
KPpid.CoderInfo.StorageClass = 'ExportedGlobal';
KPpid.Description = "PID - Proportional gain";
KPpid.Unit = "";

KIpid = Simulink.Parameter;
KIpid.Value = 1.2*K_u/T_u;
KIpid.CoderInfo.StorageClass = 'ExportedGlobal';
KIpid.Description = "PID - Integral gain";
KIpid.Unit = "";

KDpid = Simulink.Parameter;
KDpid.Value = 0.075*K_u*T_u;
KDpid.CoderInfo.StorageClass = 'ExportedGlobal';
KDpid.Description = "PID - Derivative gain";
KDpid.Unit = "";

%% Beam Properties

l_beam = Simulink.Parameter;
l_beam.Value = 5.0;
l_beam.CoderInfo.StorageClass = 'ExportedGlobal';
l_beam.Description = "Length of beam";
l_beam.Unit = "m";

J_beam = Simulink.Parameter;
J_beam.Value = 0.0005;
J_beam.CoderInfo.StorageClass = 'ExportedGlobal';
J_beam.Description = "Beam interia";
J_beam.Unit = "kg*m*m";

%% Ball Properties

m_ball = Simulink.Parameter;
m_ball.Value = 0.0025;
m_ball.CoderInfo.StorageClass = 'ExportedGlobal';
m_ball.Description = "Ball mass";
m_ball.Unit = "kg";

r_ball = Simulink.Parameter;
r_ball.Value = 0.0005;
r_ball.CoderInfo.StorageClass = 'ExportedGlobal';
r_ball.Description = "Ball radius";
r_ball.Unit = "m";

%% General Dynamics

g = Simulink.Parameter;
g.Value = 9.80665;
g.CoderInfo.StorageClass = 'ExportedGlobal';
g.Description = "Gravitational acceleration";
g.Unit = "m/s^2";

kFrs = Simulink.Parameter;
kFrs.Value = 0.001;
kFrs.CoderInfo.StorageClass = 'ExportedGlobal';
kFrs.Description = "Viscous friction coefficient";
kFrs.Unit = "N*m/(rad/s)";