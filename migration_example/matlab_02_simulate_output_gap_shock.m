
%% Load the model object

modelMatFile = fullfile("mat_files", "matlab_model.mat");
modelData = load(modelMatFile, "model");
model = modelData.model;


%% Set simulation and chart ranges

simStart = ii(1);
simEnd = ii(20);
simRange = simStart:simEnd;
chartRange = simStart-4:simEnd;


%% Create a steady-state databank

db = steadydb(model, simRange);


%% Create a shock in the steady-state databank

db.shk_y_gap(simStart) = 1;


%% Run a simulation using the model and the databank

simDb = simulate( ...
    model, db, simRange, ...
    method="firstOrder", ...
    prependInput=true ...
);


%% Combine simulated and steady-state paths for plotting

chartDb = databank.merge("horzcat", simDb, db);

ch = Chartpack( ...
    tiles=[2, 3], ...
    range=chartRange, ...
    figureTitle="GDP gap shock" ...
);

add(ch, [ ...
    "Real GDP gap: y_gap", ...
    "Real GDP growth: ad_y", ...
    "Inflation, Q/Q PA: ad_cpi", ...
    "Nominal interest rate: rs", ...
    "Real interest rate: rrs" ...
]);

chartInfo = draw(ch, chartDb);

