% Parses the spice netlist
classdef parser < handle
    properties
        file_name       (1, 1)  string = "";         % The input spice file name
        next_line       (1, 1)  int16  = 0;          % The next line number being read
        file_lines      (1, :)  string;              % Each line is separated
        envs            (1, :)  engine.environment;                
        eng             (1, 1)  engine.engine;
    end
    
    methods
        function ret = read(obj, inp_file)
            ret = error.ok;
            if(~isfile(inp_file))
                ret = error.gen_error("File " + inp_file + "does not exist");
                return
            end
            
            obj.file_name   = inp_file;
            file_text       = fileread(obj.file_name);
            obj.next_line   = 1;
            obj.envs        = [engine.environment];
            obj.eng         = engine.engine;
            obj.eng.options("mode") = 1;
            
            obj.eng.set_env(obj.envs(1));
            
            obj.file_lines      = strsplit(file_text,'\n');
        end
        
        function ret = parse(obj)
            max_lines = numel(obj.file_lines);
            
            while(obj.next_line <= max_lines)
                ret = obj.parse_line;
                if(ret.level())
                    return
                end
            end
        end
        
        function ret = parse_line(obj)
            ret = error.ok;
            
            if(numel(obj.file_lines) < obj.next_line)
                ret = error.gen_error("File read completely");
                return
            end
            
            line = split(strip(obj.file_lines(obj.next_line)), '*');
            line = char(line(1));
            
            if(numel(line) == 0)
                obj.next_line = obj.next_line + 1;
                return
            end
            
            switch(lower(line(1)))
                case '*'
                    obj.next_line  = obj.next_line + 1;
                    return
                case '.'
                    ret = obj.parse_command(line);
                    obj.next_line  = obj.next_line + 1;
                    return
                case 'c'
                    e = elements.capacitor;
                    ret = e.read_spice([obj.file_name, obj.next_line, line]);
                case 'r'
                    e = elements.resistor;
                    ret = e.read_spice([obj.file_name, obj.next_line, line]);
                case 'v'
                    
                    pattern = '^(?<id>\w+)\s+(?<n1>\w+)\s+(?<n2>\w+)\s+(?<type>\w+)(\s+)?\(.+\)$';
                    match = regexpi(line, pattern, 'names');
                    
                    if(isempty(match))
                        e = elements.v_const;
                        ret = e.read_spice([obj.file_name, obj.next_line, line]);
                    else
                        switch(lower(match.type))
                            case "pulse"
                                e = elements.v_pulse;
                                ret = e.read_spice([obj.file_name, obj.next_line, line]);
                            case "pwl"
                                e = elements.v_pwl;
                                ret = e.read_spice([obj.file_name, obj.next_line, line]);
                            case "sin"
                                e = elements.v_sin;
                                ret = e.read_spice([obj.file_name, obj.next_line, line]);
                            otherwise
                                ret = error.inp_error.inp_error(obj.file_name, obj.next_line, "Unidentified voltage source type " + match.type);
                        end
                    end
                case 'g'
                    e = elements.vccs;
                    ret = e.read_spice([obj.file_name, obj.next_line, line]);
                otherwise
                    ret = error.inp_error.inp_error(obj.file_name, obj.next_line, "Unindentified prefix");
                    obj.next_line  = obj.next_line + 1;
                    return
            end
            
            if(~ret.level())
                obj.envs(end).add_component(e);
                obj.next_line  = obj.next_line + 1;
            end
        end
        
        function ret = parse_command(obj, line)
            % NOTE : Add error detection here too!
            ret = error.ok;

            cmd_parts = split(line(2:end), ' ');
            cmd_parts(cellfun('isempty', cmd_parts)) = [];
            
            switch(lower(cmd_parts{1}))
                case "option"
                    obj.eng.add_option("option", cmd_parts{2})
                case "print"
                    obj.eng.add_node_print(cmd_parts{2})
                case "tran"
                    obj.eng.add_option("mode", 2)
                    step_size = parser.parse_number(cmd_parts{2});
                    end_time  = parser.parse_number(cmd_parts{3});
                    
                    obj.eng.add_option("step_size", step_size);
                    obj.eng.add_option("end_time", end_time);
                case "alter"
                    obj.envs(end+1) = copy(obj.envs(end));
            end
        end
    end
end
