classdef ok < error.error    
    methods
        function obj = ok()
            obj.error_type = "No error";
        end
        
        function ret = get_message(obj)
            ret = "(no error)";
        end
    end
        
    methods (Static)
        function ret = level(obj)
            ret = 0;
        end
    end
end
