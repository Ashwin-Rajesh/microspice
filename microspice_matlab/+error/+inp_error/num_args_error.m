classdef num_args_error < error.inp_error.inp_error
    methods
        function obj = num_args_error(inp_file, inp_line, inp_act, inp_req)
            obj@error.inp_error.inp_error(inp_file, inp_line, " Mismatch in number of arguments (" + inp_act + " given, " + inp_req + " required)");
        end
    end
end
