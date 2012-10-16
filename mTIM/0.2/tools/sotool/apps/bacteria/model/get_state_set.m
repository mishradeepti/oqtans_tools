function STATES = get_state_set(PAR)
% STATES = get_state_set(PAR)
%
% Returns the set of states of the graphical model.
%
% PAR -- a struct of parameters specified in setup_hmsvm_training.m and
%   train_hmsvm.m
%
% written by Georg Zeller, MPI Tuebingen, Germany, 2007-2008

STATES            = [];
STATES.start      = 1;
STATES.stop       = 2;
STATES.intergenic = 3;
STATES.startCodon = 4;
STATES.stopCodon  = 5;
STATES.exonic1    = 6;
STATES.exonic2    = 7;
STATES.exonic3    = 8;
