classdef engine < handle
    properties
        env         (1, 1)  engine.environment;     % The ciruit environment
        options             containers.Map;         % Options
        print_nodes (1, :)  string;                 % List of node names to be printed
        
        time                double = 0;
        
        data_dc     (1, :)  double;                 % Results of DC simulation
        data_trans          double;                 % Results of the transient simulation
    end
    
    methods
        function obj = engine()
            obj.print_nodes = [];
        end
        
        function set_env(obj, inp_env)
            obj.env = inp_env;
        end
        
        function ret = run(obj)
            switch(obj.options("mode"))
                case 1
                    disp("DC not implemented yet")
                case 2
                    obj.run_trans(obj.options("end_time"), obj.options("step_size"));
                    ret = containers.Map("keyType", 'char', "ValueType", 'any');
                    
                    for n = obj.print_nodes
                        if(n == "0")
                            ret(n) = zeros([size(obj.data_trans, 1), 1]);
                        else
                            ret(n) = obj.data_trans(:,obj.env.node_dict(n) - 1);
                        end
                        ret("time") = obj.data_trans(:,end);
                    end
                otherwise
            end
        end
        
        function run_trans(obj, end_time, step_size)
            timestamps = linspace(0, end_time, 1 + end_time / step_size);
            
            obj.data_trans = [[]];
            
            soln = obj.solve_dc();
            obj.data_dc = soln;
            obj.env.set_node_vals(soln);
            obj.env.update_comp_states(0);
            obj.data_trans(end+1, :) = soln;            

            for t = timestamps(2:end)
                soln = obj.solve_trans_step(step_size);
                obj.env.set_node_vals(soln);
                obj.env.update_comp_states(t);
                obj.data_trans(end+1, :) = soln;            
            end
            obj.data_trans(:,end+1) = timestamps;
        end
        
        function soln_vec = solve_trans_step(obj, step_size)
            mat = obj.env.get_mat_trans(step_size);
            lhs_mat = mat([1:end], [1:end-1]);
            rhs_vec = mat([1:end], [end]);
            
            soln_vec = lhs_mat\rhs_vec;
        end
        
        function soln_vec = solve_dc(obj)
            mat = obj.env.get_mat_dc;
            lhs_mat = mat([1:end], [1:end-1]);
            rhs_vec = mat([1:end], [end]);
            
            soln_vec = lhs_mat\rhs_vec;
        end
        
        % Add an option to the settings
        function add_option(obj, opt_key, opt_val)
            obj.options(opt_key) = opt_val;
        end
        
        function add_node_print(obj, node_identifier)
            pattern = '^(v|i|V|I)\((\w+)\)$';

            % check if the input string matches the pattern
            tokens = regexp(node_identifier, pattern, 'tokens');

            if ~isempty(tokens)
                % extract the matching group
                x = tokens{1}{2};
                t = lower(tokens{1}{1});
                switch(t)
                    case 'v'
                        node = x;
                    case 'i'
                        node = "_I_" + x;
                end
                if(obj.env.node_dict.isKey(node))
                    obj.print_nodes(end+1) = node;
                end
            else
                disp('Input string does not match the pattern V(x) or I(x).');
            end
        end
    end
end
