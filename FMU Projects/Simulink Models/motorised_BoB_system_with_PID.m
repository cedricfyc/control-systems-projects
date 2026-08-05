%% Position controller
KPp = Simulink.Parameter;
KPp.Value = 12.0;
KPp.CoderInfo.StorageClass = 'ExportedGlobal';
KPp.Description = "Position controller proportional gain";
KPp.Unit = "";

KIp = Simulink.Parameter;
KIp.Value = 3.0;
KIp.CoderInfo.StorageClass = 'ExportedGlobal';
KIp.Description = "Position controller integral gain";
KIp.Unit = "";

KDp = Simulink.Parameter;
KDp.Value = 3.0;
KDp.CoderInfo.StorageClass = 'ExportedGlobal';
KDp.Description = "Position controller integral gain";
KDp.Unit = "";

%% Current controller
KPi = Simulink.Parameter;
KPi.Value = 1.50;
KPi.CoderInfo.StorageClass = 'ExportedGlobal';
KPi.Description = "Current controller proportional gain";
KPi.Unit = "";

KIi = Simulink.Parameter;
KIi.Value = 150;
KIi.CoderInfo.StorageClass = 'ExportedGlobal';
KIi.Description = "Current controller integral gain";
KIi.Unit = "";

KDi = Simulink.Parameter;
KDi.Value = 0.005;
KDi.CoderInfo.StorageClass = 'ExportedGlobal';
KDi.Description = "Current controller derivative gain";
KDi.Unit = "";

%% Velocity controller 
KPv = Simulink.Parameter;
KPv.Value = 3.49;
KPv.CoderInfo.StorageClass = 'ExportedGlobal';
KPv.Description = "Velocity controller proportional gain";
KPv.Unit = "";

KIv = Simulink.Parameter;
KIv.Value = 250.0;
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

K_u = 10.0;
T_u = 0.7428;

KPpid = Simulink.Parameter;
KPpid.Value = 0.6*K_u;
KPpid.CoderInfo.StorageClass = 'ExportedGlobal';
KPpid.Description = "PID - Proportional Gain";
KPpid.Unit = "";

KIpid = Simulink.Parameter;
KIpid.Value = 1.2*K_u/T_u;
KIpid.CoderInfo.StorageClass = 'ExportedGlobal';
KIpid.Description = "PID - Integral Gain";
KIpid.Unit = "";

KDpid = Simulink.Parameter;
KDpid.Value = 0.075*K_u*T_u;
KDpid.CoderInfo.StorageClass = 'ExportedGlobal';
KDpid.Description = "PID - Derivative Gain";
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
m_ball.Description = "Ball Mass";
m_ball.Unit = "kg";

r_ball = Simulink.Parameter;
r_ball.Value = 0.0005;
r_ball.CoderInfo.StorageClass = 'ExportedGlobal';
r_ball.Description = "Ball Radius";
r_ball.Unit = "m";

c = Simulink.Parameter;
c.Value = 0.001;
c.CoderInfo.StorageClass = 'ExportedGlobal';
c.Description = "Sliding Friction Coefficient";
c.Unit = "N*m/(rad/s)";

%% General Dynamics

g = Simulink.Parameter;
g.Value = 9.80665;
g.CoderInfo.StorageClass = 'ExportedGlobal';
g.Description = "PID - Derivative Gain";
g.Unit = "m/s^2";