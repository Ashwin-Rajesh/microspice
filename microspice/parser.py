import microspice.engine        as engine
import microspice.error.error   as error
import microspice.environment   as environment
import microspice.elements      as elements
from   microspice.utils         import *

import os.path
import re
import copy

# This class parses a file and populates the engine and environment
#       with components, connectivity and simulation settings
class Parser:
    def __init__(self):
        self.file_name  = ""
        self.next_line  = 0
        self.file_lines = []
        self.envs       = []
        self.eng        = engine.Engine()

    # Read a netlist into buffer and initialize variables
    def read(self, inp_file):
        ret = error.OkError()

        # Check if the file exists
        if not os.path.isfile(inp_file):
            ret = error.GenError("File " + inp_file + " does not exist")
            return ret

        # Set the filename and line counts (used for debugging)
        self.file_name = inp_file
        self.next_line = 1
        
        # Initialize the engine and environment 
        self.envs      = [environment.Environment()]        
        self.eng       = engine.Engine()
        self.eng.options["mode"] = 1
        self.eng.set_env(self.envs[0])

        # Read the file
        with open(self.file_name, 'r') as file:
            self.file_lines = file.read().split('\n')
        
        return ret

    # Parse the whole netlist
    def parse(self):
        max_lines = len(self.file_lines)

        # Iterate through all the lines
        while self.next_line <= max_lines:
            ret = self.parse_line()
            if ret.level():
                return ret
            
        return ret

    # Parse a single line of the spice netlist
    def parse_line(self):
        ret = error.OkError()

        # Last line (should not happen unless function is called after running "parse()")
        if len(self.file_lines) < self.next_line:
            ret = error.GenError("File read completely")
            return ret

        # Read file, remove comments and leading and trailing whitespace
        line = self.file_lines[self.next_line - 1].split('*')[0].strip()
        if len(line) == 0:
            self.next_line += 1
            return ret

        # Decide the element type or the command 
        switch_case = line[0].lower()
        # Comment
        if switch_case == '*':
            self.next_line += 1
            return ret
        # Command
        elif switch_case == '.':
            ret = self.parse_command(line)
            self.next_line += 1
            return ret
        # Capacitor
        elif switch_case == 'c':
            e = elements.Capacitor()
            ret = e.read_spice([self.file_name, self.next_line, line])
        # Resistor
        elif switch_case == 'r':
            e = elements.Resistor()
            ret = e.read_spice([self.file_name, self.next_line, line])
        # Voltage source
        elif switch_case == 'v':
            pattern = r'^(?P<id>\w+)\s+(?P<n1>\w+)\s+(?P<n2>\w+)\s+(?P<type>\w+)(\s+)?\(.+\)$'
            match = re.match(pattern, line)

            if match is None:
                e = elements.VConst()
                ret = e.read_spice([self.file_name, self.next_line, line])
            else:
                voltage_type = match.group('type').lower()
                if voltage_type == "pulse":
                    e = elements.VPulse()
                    ret = e.read_spice([self.file_name, self.next_line, line])
                elif voltage_type == "pwl":
                    e = elements.VPWL()
                    ret = e.read_spice([self.file_name, self.next_line, line])
                elif voltage_type == "sin":
                    e = elements.VSin()
                    ret = e.read_spice([self.file_name, self.next_line, line])
                else:
                    ret = error.InpError(self.file_name, self.next_line,
                                         "Unidentified voltage source type " + voltage_type)
        # VCCS (Voltage controlled current source)
        elif switch_case == 'g':
            e = elements.VCCS()
            ret = e.read_spice([self.file_name, self.next_line, line])
        # Not implemented!
        else:
            ret = error.InpError(self.file_name, self.next_line, "Unidentified prefix")
            self.next_line += 1
            return ret

        # Error detection
        if not ret.level():
            self.envs[-1].add_component(e)
            self.next_line += 1

        return ret

    # Parse a spice command (starts with .)
    def parse_command(self, line):
        ret = error.OkError()

        # Extract the components of the command (separated by spaces)
        cmd_parts = line[1:].split(' ')
        cmd_parts = [part for part in cmd_parts if part != ""]

        switch_case = cmd_parts[0].lower()

        # SPICE commands
        if switch_case == "option":
            # Options are added to the options dictionary in the engine
            self.eng.add_option("option", cmd_parts[1])
        
        elif switch_case == "print":
            # Nodes to be printed are added to the print list in the engine
            self.eng.add_node_print(cmd_parts[1])
        
        elif switch_case == "tran":
            # For setting transient mode, the "mode" option is set to 2 and other
            #       settings are added to the options dictionary
            step_size   = parse_number(cmd_parts[1])
            end_time    = parse_number(cmd_parts[2])
            
            self.eng.add_option("mode", 2)
            self.eng.add_option("step_size", step_size)
            self.eng.add_option("end_time", end_time)

        elif switch_case == "alter":
            # The alter command sets up one more simulation by creating a copy of the most recent environment
            self.envs.append(copy.deepcopy(self.envs[-1]))

        return ret
