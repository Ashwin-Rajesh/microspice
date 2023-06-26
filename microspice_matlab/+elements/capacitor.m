classdef capacitor < elements.element
    properties
        capacitance         (1, 1)      double;
        voltage             (1, 1)      double;
    end
    
    methods
        function ret = read_spice(obj, spice_inp)
            ret = error.ok;

            spice_line = spice_inp(3);
            line_num   = str2num(spice_inp(2));
            file_name  = spice_inp(1);

            inp = split(spice_line, ' ');
            inp(cellfun('isempty', inp)) = [];
            
            if(numel(inp) ~= 4)
                ret = error.inp_error.num_args_error(file_name, line_num, numel(inp)-1, 3);
                return;
            end
            
            obj.id = inp(1);
            obj.nodes = [inp(2), inp(3)];
            obj.capacitance = parser.parse_number(inp(4));
            obj.voltage = 0;
            
            if(isnan(obj.capacitance))
                ret = error.inp_error.inp_error(file_name, line_num, "Argument '" + inp(4) + "' is not valid numeric format");
            end
        end
        
        function stamp = stamp_dc(obj)
            stamp = [
                [0 0 0];                                % +N
                [0 0 0]                                 % -N
                ];
        end
        
        function stamp = stamp_ac(obj, freq)
            temp = 1i * freq * obj.capacitance;
            stamp = [
                [temp,  -temp,  0];                     % +N
                [-temp, temp,   0]                      % -N
                ];
        end
        
        function stamp = stamp_trans(obj, h)
            temp = obj.capacitance / h;
            stamp = [
                [temp,  -temp,  temp * obj.voltage];
                [-temp, temp,   -temp * obj.voltage]
            ];
        end
        
        function update_state(obj, time, state_val_map)
            obj.voltage = state_val_map(obj.nodes(1)) - state_val_map(obj.nodes(2));
        end
    end
end
