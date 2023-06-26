# Root class for error handling
class Error:
    def __init__(self, *args):
        self.error_type = "Default error"

    def to_str(self):
        return self.error_type + " - " + self.get_message()

    @staticmethod
    def level():
        return 1

    def get_message(self):
        pass

# Generic error message
class GenError(Error):
    def __init__(self, inp_msg):
        super().__init__()
        self.error_type = "Error"
        self.message = inp_msg
    
    def get_message(self):
        return self.message

# No error return object
class OkError(Error):
    def __init__(self):
        super().__init__()
        self.error_type = "No error"
    
    def get_message(self):
        return "(no error)"
    
    def level(self):
        return 0
