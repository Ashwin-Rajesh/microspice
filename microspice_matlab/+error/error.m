classdef error
    properties
        error_type = "Default error";
    end
    
    methods
        function obj = error(varargin)
        end
        
        function ret = to_str(obj)
            ret = obj.error_type + " - " + obj.get_message();
        end
    end
        
    methods (Static)
        function ret = level            % Gets the error level
            ret = 1;
        end
    end
    
    methods (Abstract)
        get_message(obj);
    end
end
