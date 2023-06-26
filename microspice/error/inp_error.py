from microspice.error.error import Error

class InputError(Error):
    def __init__(self, inp_file, inp_line, inp_msg):
        super().__init__()
        self.error_type = "Input error"
        self.file_name  = inp_file
        self.line_num   = inp_line
        self.message    = inp_msg
    
    def get_message(self):
        return f"{self.file_name} line {self.line_num} : {self.message}"

class NumArgsError(InputError):
    def __init__(self, inp_file, inp_line, inp_act, inp_req):
        super().__init__(inp_file, inp_line, f"Mismatch in number of arguments ({inp_act} given, {inp_req} required)")
