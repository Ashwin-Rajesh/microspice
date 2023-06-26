classdef v_sin < elements.element
    properties
        time                (1, 1)      double;
        
        offset_v            (1, 1)      double;
        amplitude_v         (1, 1)      double;
        init_delay          (1, 1)      double;
        frequency           (1, 1)      double;
        damp_factor         (1, 1)      double;
        phase               (1, 1)      double;
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
                ret = error.inp_error.inp_error(file_name, line_num, "Match for voltage type SIN failed");
                return
            end
                        
            obj.id      = match.id;
            obj.nodes   = [match.n1, match.n2, "_I_" + obj.id];
            obj.time    = 0;
            
            options     = strsplit(match.options, {' ',','},'CollapseDelimiters',true);
            options(cellfun('isempty', options)) = [];

            if(numel(options) ~= 6)
                ret = error.inp_error.inp_error(file_name, line_num, "The number of options for sine must be 7");
                return;
            end
            
            options = arrayfun(@parser.parse_number, options);
            
            if(any(isnan(options)))
                ret = error.inp_error.inp_error(file_name, line_num, "All options for sine must be numeric");
                return;
            end
            
            obj.offset_v            = options(1);
            obj.amplitude_v         = options(2);
            obj.frequency           = options(3);
            obj.init_delay          = options(4);
            obj.damp_factor         = options(5);
            obj.phase               = options(6);
        end
        
        function stamp = stamp_dc(obj)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.get_voltage(0)]
                ];
        end
        
        function stamp = stamp_ac(obj, freq)
            stamp = [
                    [0, 0, 1, 0];
                    [0, 0,-1, 0];
                    [1,-1, 0, obj.amplitude_v]
                ];
        end
        
        function v = get_voltage(obj, t)
            t_shift = t - obj.init_delay;
            if(t < obj.init_delay)
                t_shift = 0;
            end
            exp_comp = exp(obj.damp_factor * (t_shift));
            
            sin_comp = sin((2 * pi * obj.frequency * (t_shift)) + (obj.phase * pi / 180));
            
            v = obj.offset_v + (obj.amplitude_v * sin_comp * exp_comp);
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
