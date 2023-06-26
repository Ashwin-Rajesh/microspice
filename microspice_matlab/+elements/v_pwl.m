classdef v_pwl < elements.element
    properties
        time                (1, 1)      double;
        
        table               (2, :)      double;
        
        curr_idx            (1, 1)      int16;
    end
    
    methods
        function ret = read_spice(obj, spice_inp)
            ret = error.ok;

            spice_line = spice_inp(3);
            line_num   = str2num(spice_inp(2));
            file_name  = spice_inp(1);
            
            % Matching using regular expression
            pattern = '^(?<id>\w+)\s+(?<n1>\w+)\s+(?<n2>\w+)\s+(?<type>\w+)(\s+)?\((?<options>.+)\)$';
            match = regexpi(spice_line, pattern, 'names');

            if(isempty(match))
                ret = error.inp_error.inp_error(file_name, line_num, "Match for voltage type PWL failed");
                return
            end
                        
            obj.id      = match.id;
            obj.nodes   = [match.n1, match.n2, "_I_" + obj.id];
            obj.time    = 0;
            obj.curr_idx = 1;
            
            options     = strsplit(match.options, {' ',','},'CollapseDelimiters',true);
            options(cellfun('isempty', options)) = [];

            if(mod(numel(options), 2) ~= 0)
                ret = error.inp_error.inp_error(file_name, line_num, "The number of options for pwl must be even");
                return;
            end
            
            options = arrayfun(@parser.parse_number, options);
            
            if(any(isnan(options)))
                ret = error.inp_error.inp_error(file_name, line_num, "All options for pulse must be numeric");
                return;
            end
            obj.table   = zeros(2, numel(options)/2);
            
            obj.table(1,:) = options(1:2:end);
            obj.table(2,:) = options(2:2:end);
        end
        
        function stamp = stamp_dc(obj)
            init_v = obj.table(2, 1);
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, init_v]
                ];
        end
        
        function stamp = stamp_ac(obj, freq)
            init_v = obj.table(2, 1);
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, init_v]
                ];
        end
        
        function v = get_voltage(obj, t)
            while(obj.curr_idx <= numel(obj.table) / 2 && obj.table(1, obj.curr_idx) < t)
                obj.curr_idx = obj.curr_idx + 1;
            end
            
            if(obj.curr_idx == 1)
                v = obj.table(2, 1);
            elseif(obj.curr_idx == (numel(obj.table) / 2) + 1)
                v = obj.table(2, end);
            else
                v = obj.table(2, obj.curr_idx - 1) + ((obj.table(2, obj.curr_idx) - obj.table(2, obj.curr_idx - 1)) * (t - obj.table(1, obj.curr_idx-1)) / (obj.table(1, obj.curr_idx) - obj.table(1, obj.curr_idx - 1)));
            end
        end
        
        function update_state(obj, time, state_val_map)
            obj.time = time;
        end

        function stamp = stamp_trans(obj, h)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.get_voltage(obj.time)]
                ];
        end
    end
end
