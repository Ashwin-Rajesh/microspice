classdef inp_error < error.error
    properties
        file_name   (1, 1)  string;     % The name of file where error was detected
        line_num    (1, 1)  int32;      % The line number of the input file at which error was detected
        message     (1, 1)  string;     % The message to be encoded
    end
    
    methods
        function obj = inp_error(inp_file, inp_line, inp_msg)
            obj.error_type = "Input error";
            obj.file_name = inp_file;
            obj.line_num  = inp_line;
            obj.message   = inp_msg;
        end
        
        function ret = get_message(obj)
            ret = obj.file_name + " line " + obj.line_num + " : " + obj.message;
        end
    end
end
