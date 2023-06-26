# MIT License

# Copyright (c) 2023 Ashwin Rajesh

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import microspice.engine        as engine
# import microspice.error.error   as error
import microspice.errors        as errors
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
        # Check if the file exists
        if not os.path.isfile(inp_file):
            raise errors.uSpiceError(f"File {inp_file} could not be opened")
            
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
        
    # Parse the whole netlist
    def parse(self):
        max_lines = len(self.file_lines)

        # Iterate through all the lines
        while self.next_line <= max_lines:
            self.parse_line()
            
    # Parse a single line of the spice netlist
    def parse_line(self):
        # Last line (should not happen unless function is called after running "parse()")
        if len(self.file_lines) < self.next_line:
            raise errors.uSpiceError("File read completely")
            
        # Read file, remove comments and leading and trailing whitespace
        line = self.file_lines[self.next_line - 1].split('*')[0].strip()
        if len(line) == 0:
            self.next_line += 1
            return
        
        # Decide the element type or the command 
        switch_case = line[0].lower()
        # Comment
        if switch_case == '*':
            pass
        # Command
        elif switch_case == '.':
            self.parse_command(line)
        else:
            # Add elements
            # Capacitor
            if switch_case == 'c':
                e = elements.Capacitor()
            # Resistor
            elif switch_case == 'r':
                e = elements.Resistor()
            # Voltage source
            elif switch_case == 'v':
                pattern = r'^(?P<id>\w+)\s+(?P<n1>\w+)\s+(?P<n2>\w+)\s+(?P<type>\w+)(\s+)?\(.+\)$'
                match = re.match(pattern, line)

                if match is None:
                    e = elements.VConst()
                else:
                    voltage_type = match.group('type').lower()
                    if voltage_type == "pulse":
                        e = elements.VPulse()
                    elif voltage_type == "pwl":
                        e = elements.VPWL()
                    elif voltage_type == "sin":
                        e = elements.VSin()
                    else:
                        raise errors.NetlistError(self.file_name, self.next_line, f"Unidentified voltage source type {voltage_type}")

            # VCCS (Voltage controlled current source)
            elif switch_case == 'g':
                e = elements.VCCS()
            # Not implemented!
            else:
                raise errors.NetlistError(self.file_name, self.next_line, "Unidetified prefix")
            
            try:
                e.read_spice(line)
            except errors.SyntaxError as e:
                raise errors.NetlistError(self.file_name, self.next_line, e.message + '\n' + line)
            
            self.envs[-1].add_component(e)
        
        self.next_line += 1

    # Parse a spice command (starts with .)
    def parse_command(self, line):
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
