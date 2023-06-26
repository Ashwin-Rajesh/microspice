classdef v_pulse < elements.element
    properties
        time                (1, 1)      double;
        
        init_v              (1, 1)      double;
        final_v             (1, 1)      double;
        init_delay          (1, 1)      double;
        rise_time           (1, 1)      double;
        fall_time           (1, 1)      double;
        pulse_width         (1, 1)      double;
        period              (1, 1)      double;
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
                ret = error.inp_error.inp_error(file_name, line_num, "Match for voltage type PULSE failed");
                return
            end
                        
            obj.id      = match.id;
            obj.nodes   = [match.n1, match.n2, "_I_" + obj.id];
            obj.time    = 0;
            
            options     = strsplit(match.options, {' ',','},'CollapseDelimiters',true);
            options(cellfun('isempty', options)) = [];

            if(numel(options) ~= 7)
                ret = error.inp_error.inp_error(file_name, line_num, "The number of options for pulse must be 7");
                return;
            end
            
            options = arrayfun(@parser.parse_number, options);
            
            if(any(isnan(options)))
                ret = error.inp_error.inp_error(file_name, line_num, "All options for pulse must be numeric");
                return;
            end
            
            obj.init_v = options(1);
            obj.final_v = options(2);
            obj.init_delay = options(3);
            obj.rise_time = options(4);
            obj.fall_time = options(5);
            obj.pulse_width = options(6);
            obj.period = options(7);
        end
        
        function stamp = stamp_dc(obj)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.init_v]
                ];
        end
        
        function stamp = stamp_ac(obj, freq)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.init_v]
                ];
        end
        
        function v = get_voltage(obj, t)
            if(t < obj.init_delay)
                v = obj.init_v;
                return;
            end
            t_cyc = mod(t - obj.init_delay, obj.period);
            
            if(t_cyc < obj.rise_time)
                v = obj.init_v + (obj.final_v - obj.init_v) * t_cyc / obj.rise_time;
            elseif(t_cyc < obj.rise_time + obj.pulse_width)
                v = obj.final_v;
            elseif(t_cyc < obj.rise_time + obj.pulse_width + obj.fall_time)
                v = obj.final_v + (obj.init_v - obj.final_v) * (t_cyc - (obj.rise_time + obj.pulse_width)) / obj.fall_time;
            else
                v = obj.init_v;
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
