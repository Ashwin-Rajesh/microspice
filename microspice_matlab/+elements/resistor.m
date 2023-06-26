classdef resistor < elements.element
    properties
        resistance          (1, 1)      double;
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
            obj.resistance = parser.parse_number(inp(4));
            
            if(isnan(obj.resistance))
                ret = error.inp_error.inp_error(file_name, line_num, "Argument '" + inp(4) + "' is not valid numeric format");
            end
            return
        end
        
        function stamp = stamp_dc(obj)
            stamp = [
                [1/obj.resistance, -1/obj.resistance,   0];         % N+
                [-1/obj.resistance, 1/obj.resistance,   0]          % N-
                ];
        end
        
        function stamp = stamp_ac(obj, freq)
            stamp = [
                [1/obj.resistance, -1/obj.resistance,   0];         % N+
                [-1/obj.resistance, 1/obj.resistance,   0]          % N-
                ];
        end
        
        function stamp = stamp_trans(obj, h)
            stamp = [
                [1/obj.resistance, -1/obj.resistance,   0];         % N+
                [-1/obj.resistance, 1/obj.resistance,   0]          % N-
                ];
        end
    end
end
