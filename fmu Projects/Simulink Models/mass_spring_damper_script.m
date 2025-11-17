model = 'mass_spring_damper';

load_system(model);

m = Simulink.Parameter(1);
m.CoderInfo.StorageClass = 'SimulinkGlobal';

c = Simulink.Parameter(100);
c.CoderInfo.StorageClass = 'SimulinkGlobal';

d = Simulink.Parameter(5);
d.CoderInfo.StorageClass = 'SimulinkGlobal';

set_param(model, 'SolverType', 'Fixed-step', 'FixedStep', '0.01', 'StopTime', '10');

set_param(model, 'DefaultParameterBehavior', 'Tunable');