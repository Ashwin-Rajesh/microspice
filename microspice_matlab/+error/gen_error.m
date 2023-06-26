classdef gen_error < error.error
    properties
        message     (1, 1) string;
    end
    
    methods
        function obj = gen_error(inp_msg)
            obj.error_type = "Error";
            obj.message    = inp_msg;
        end
        
        function ret = get_message(obj)
            ret = obj.message;
        end
    end
end
