% Contains all the components and nodes
classdef environment < matlab.mixin.Copyable
    properties
        num_nodes       int32 = 1;              % The number of nodes
        
        comp_dict       containers.Map;         % Map between component names and their instances
        node_dict       containers.Map;         % Map between node name (incl virtual nodes) to the index
        
        node_vals       containers.Map;         % Value of node variables
        comp_node_idx   containers.Map;         % Map between componenet names and a list of environment indices of each node of the component (for use in stamping)
    end
    
    methods
        % Constructor
        function obj = environment
            obj.comp_dict = containers.Map;
            obj.node_dict = containers.Map(["0"], [1]);
            obj.node_vals = containers.Map(["0"], [0]);
            obj.comp_node_idx = containers.Map;
        end
        
        % Add components to the environment
        function add_component(obj, comp)
            obj.comp_dict(comp.id) = comp;
            
            node_idx_ls = [];
            for node = comp.nodes
                if((~obj.node_dict.isKey(node)))
                    obj.num_nodes = obj.num_nodes + 1;
                    obj.node_dict(node) = obj.num_nodes;
                end
                node_idx_ls(end+1) = obj.node_dict(node);
            end
            obj.comp_node_idx(comp.id) = node_idx_ls;
        end
        
        % Form the matrix to solve DC
        function mat = get_mat_dc(obj)
            stamp_mat = zeros(obj.num_nodes, obj.num_nodes+1);
            
            components = obj.comp_dict.values;
            for i = 1:obj.comp_dict.Count
                comp     = components{i};
                
                index_vec = obj.comp_node_idx(comp.id);
                
                stamp = comp.stamp_dc();
                for j = 1:numel(index_vec)
                    stamp_mat(index_vec(j), [index_vec end]) = stamp_mat(index_vec(j), [index_vec end]) + stamp(j,:);
                end
            end
            
            mat = stamp_mat([2:end], [2:end]);
        end
        
        % Form the matrix to solve transient
        function mat = get_mat_trans(obj, step_size)
            stamp_mat = zeros(obj.num_nodes, obj.num_nodes+1);
            
            components = obj.comp_dict.values;
            for i = 1:obj.comp_dict.Count
                comp     = components{i};
                
                index_vec = obj.comp_node_idx(comp.id);

                stamp = comp.stamp_trans(step_size);
                for j = 1:numel(index_vec)
                    stamp_mat(index_vec(j), [index_vec end]) = stamp_mat(index_vec(j), [index_vec end]) + stamp(j,:);
                end
            end
            
            mat = stamp_mat([2:end], [2:end]);
        end
        
        % Set node values in the node_vals dictionary from the solution vector
        function set_node_vals(obj, soln_vec)
            for n = obj.node_dict.keys
                n = n{1};
                if(n ~= "0")
                    obj.node_vals(n) = soln_vec(obj.node_dict(n)-1);
                end
            end
        end
        
        % Update component states using the node_vals dictionary and time
        function update_comp_states(obj, time)
            components = obj.comp_dict.values;
            
            for i = 1:obj.comp_dict.Count
                comp     = components{i};
                
                comp.update_state(time, obj.node_vals);
            end
        end
    end
    
    methods (Access = protected)        
        % Deep copy (for alter command).
        function cp = copyElement(obj)
            cp = engine.environment;
            for comp = obj.comp_dict.values
                cp.add_component(copy(comp{1}))
            end
        end
    end
end
