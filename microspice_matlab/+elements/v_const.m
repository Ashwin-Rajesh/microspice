classdef v_const < elements.element
    properties
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
                        
            obj.id = inp(1);
            obj.nodes = [inp(2), inp(3), "_I_" + obj.id];
            num_val = parser.parse_number(inp(4));

            % Check if the next parameter is numeric
            if(~isnan(num_val))
                obj.voltage = num_val;
            else
                ret = error.inp_error.inp_error(file_name, line_num, "Argument '" + inp(4) + "' is not valid numeric format");
            end
        end
        
        function stamp = stamp_dc(obj)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.voltage]
                ];
        end
        
        function stamp = stamp_ac(obj, freq)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.voltage]
                ];
        end
        
        function stamp = stamp_trans(obj, h)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.voltage]
                ];
        end
    end
end
