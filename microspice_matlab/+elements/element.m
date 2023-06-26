% Defines the base class for a circuit element instance
classdef element < matlab.mixin.Copyable
    properties
        % Internal constants
        id          (1, 1) string;         % Identifier (name) of the instance
        
        % Circuit connectivity
        nodes       (1, :) string;         % Actual and virtual (like branch currents) nodes
    end
    
    methods
        ret = read_spice(obj, spice_inp)            % Read a line from spice and set the values
        
        stmp = stamp_dc(obj)                        % Generate the stamp matrix for DC

        stmp = stamp_ac(obj, freq)                  % Generate the stamp matrix for AC
        
        stmp = stamp_trans(obj, h)                  % Generate the stamp matrix for transient simulation
        
        function update_state(obj, time, state_val_map)   % Load the state variables the node value dictionary
        end
   end
end
