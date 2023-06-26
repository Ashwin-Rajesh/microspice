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

from microspice.utils           import *
from microspice.errors          import *

import numpy as np
from   copy import copy

class Element():
    def __init__(self):
        # Internal constants
        self.id = ''         # Identifier (name) of the instance
        
        # Circuit connectivity
        self.nodes = []      # Actual and virtual (like branch currents) nodes
    
    def read_spice(self, spice_inp):
        # Read a line from spice and set the values
        pass
    
    def stamp_dc(self):
        # Generate the stamp matrix for DC
        pass
    
    def stamp_ac(self, freq):
        # Generate the stamp matrix for AC
        pass
    
    def stamp_trans(self, h):
        # Generate the stamp matrix for transient simulation
        pass
    
    def update_state(self, time, state_val_map):
        # Load the state variables the node value dictionary
        pass

class Capacitor(Element):
    def __init__(self):
        super().__init__()
        self.capacitance = 0.0
        self.voltage = 0.0
    
    def read_spice(self, spice_line):
        
        inp = spice_line.split(' ')
        inp = [item for item in inp if item != '']
        
        if len(inp) != 4:
            raise SyntaxError(f"3 options expected, only {len(inp) -1} received")
            # ret = NumArgsError(file_name, line_num, len(inp)-1, 3)
            
        self.id = inp[0]
        self.nodes = [inp[1], inp[2]]
        self.capacitance = parse_number(inp[3])
        self.voltage = 0.0
            
    def stamp_dc(self):
        stamp = [
            [0, 0, 0],  # +N
            [0, 0, 0]   # -N
        ]
        return np.asarray(stamp)
    
    def stamp_ac(self, freq):
        temp = 1j * freq * self.capacitance
        stamp = [
            [temp, -temp, 0],   # +N
            [-temp, temp, 0]    # -N
        ]
        return np.asarray(stamp)
    
    def stamp_trans(self, h):
        temp = self.capacitance / h
        stamp = [
            [temp, -temp, temp * self.voltage],
            [-temp, temp, -temp * self.voltage]
        ]
        return np.asarray(stamp)
    
    def update_state(self, time, state_val_map):
        self.voltage = state_val_map[self.nodes[0]] - state_val_map[self.nodes[1]]

class Resistor(Element):
    def __init__(self):
        super().__init__()
        self.resistance = 0.0
    
    def read_spice(self, spice_line):
        inp = spice_line.split(' ')
        inp = [item for item in inp if item != '']
        
        if len(inp) != 4:
            raise SyntaxError(f"3 options expected, only {len(inp) -1} received")
        
        self.id = inp[0]
        self.nodes = [inp[1], inp[2]]
        self.resistance = parse_number(inp[3])
            
    def stamp_dc(self):
        stamp = [
            [1/self.resistance, -1/self.resistance, 0],    # N+
            [-1/self.resistance, 1/self.resistance, 0]     # N-
        ]
        return np.asarray(stamp)
    
    def stamp_ac(self, freq):
        stamp = [
            [1/self.resistance, -1/self.resistance, 0],    # N+
            [-1/self.resistance, 1/self.resistance, 0]     # N-
        ]
        return np.asarray(stamp)
    
    def stamp_trans(self, h):
        stamp = [
            [1/self.resistance, -1/self.resistance, 0],    # N+
            [-1/self.resistance, 1/self.resistance, 0]     # N-
        ]
        return np.asarray(stamp)

class VConst(Element):
    def __init__(self):
        super().__init__()
        self.voltage = 0.0
    
    def read_spice(self, spice_line):
        inp = spice_line.split(' ')
        inp = [item for item in inp if item != '']
        
        self.id         = inp[0]
        self.nodes      = [inp[1], inp[2], "_I_" + self.id]
        self.voltage    = parse_number(inp[3])
        
    def stamp_dc(self):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.voltage]
        ]
        return np.asarray(stamp)
    
    def stamp_ac(self, freq):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.voltage]
        ]
        return np.asarray(stamp)
    
    def stamp_trans(self, h):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.voltage]
        ]
        return np.asarray(stamp)

class VPulse(Element):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.init_v = 0.0
        self.final_v = 0.0
        self.init_delay = 0.0
        self.rise_time = 0.0
        self.fall_time = 0.0
        self.pulse_width = 0.0
        self.period = 0.0
    
    def read_spice(self, spice_line):
        pattern = r'^(?P<id>\w+)\s+(?P<n1>\w+)\s+(?P<n2>\w+)\s+(?P<type>\w+)(\s+)?\((?P<options>.+)\)$'
        match = re.match(pattern, spice_line)
        
        if match is None:
            raise SyntaxError("Match for voltage type PULSE failed")
        
        self.id = match.group('id')
        self.nodes = [match.group('n1'), match.group('n2'), "_I_" + self.id]
        self.time = 0.0
        
        options = re.split(r'\s|,', match.group('options'))
        options = [item for item in options if item != '']
        
        if len(options) != 7:
            raise SyntaxError(f"3 options expected, only {len(options) -1} received")
            
        options = [parse_number(item) for item in options]
        
        self.init_v     = options[0]
        self.final_v    = options[1]
        self.init_delay = options[2]
        self.rise_time  = options[3]
        self.fall_time  = options[4]
        self.pulse_width = options[5]
        self.period     = options[6]
            
    def stamp_dc(self):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.init_v]
        ]
        return np.asarray(stamp)
    
    def stamp_ac(self, freq):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.init_v]
        ]
        return np.asarray(stamp)
    
    def get_voltage(self, t):
        if t < self.init_delay:
            return self.init_v
            
        t_cyc = (t - self.init_delay) % self.period
        
        if t_cyc < self.rise_time:
            v = self.init_v + (self.final_v - self.init_v) * t_cyc / self.rise_time
        elif t_cyc < self.rise_time + self.pulse_width:
            v = self.final_v
        elif t_cyc < self.rise_time + self.pulse_width + self.fall_time:
            v = self.final_v + (self.init_v - self.final_v) * (t_cyc - (self.rise_time + self.pulse_width))
        else:
            v = self.init_v

        return v

    def update_state(self, time, state_val_map):
        self.time = time;
    
    def stamp_trans(self, h):
        stamp = [
            [0, 0, 1, 0],
            [0, 0,-1, 0],
            [1,-1, 0, self.get_voltage(self.time)]
        ]
        return np.asarray(stamp)

class VPWL(Element):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.table = []
        self.curr_idx = 0
    
    def read_spice(self, spice_line):
        pattern = r'^(?P<id>\w+)\s+(?P<n1>\w+)\s+(?P<n2>\w+)\s+(?P<type>\w+)(\s+)?\((?P<options>.+)\)$'
        match = re.match(pattern, spice_line)
        
        if match is None:
            raise SyntaxError("Match for voltage type VPWL failed")
            ret = InputError(file_name, line_num, "Match for voltage type PWL failed")
            return ret
        
        self.id = match.group('id')
        self.nodes = [match.group('n1'), match.group('n2'), "_I_" + self.id]
        self.time = 0.0
        self.curr_idx = 1
        
        options = re.split(r'\s|,', match.group('options'))
        options = [item for item in options if item != '']
        
        if len(options) % 2 != 0:
            raise SyntaxError("Expected an even nnumber of options for VPWL")
        
        options = [parse_number(item) for item in options]
        
        self.table = [[options[i], options[i+1]] for i in range(0, len(options), 2)]
        
    def stamp_dc(self):
        init_v = self.table[0][1]
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, init_v]
        ]
        return np.asarray(stamp)
    
    def stamp_ac(self, freq):
        init_v = self.table[0][1]
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, init_v]
        ]
        return np.asarray(stamp)
    
    def get_voltage(self, t):
        while self.curr_idx <= len(self.table) and self.table[self.curr_idx - 1][0] < t:
            self.curr_idx += 1
        
        if self.curr_idx == 1:
            v = self.table[0][1]
        elif self.curr_idx == len(self.table) + 1:
            v = self.table[-1][1]
        else:
            v = self.table[self.curr_idx - 2][1] + ((self.table[self.curr_idx - 1][1] - self.table[self.curr_idx - 2][1]) * (t - self.table[self.curr_idx - 2][0]) / (self.table[self.curr_idx - 1][0] - self.table[self.curr_idx - 2][0]))
        
        return v
    
    def update_state(self, time, state_val_map):
        self.time = time
    
    def stamp_trans(self, h):
        stamp = [
            [0, 0, 1, 0],
            [0, 0,-1, 0],
            [1,-1, 0, self.get_voltage(self.time)]
        ]
        return np.asarray(stamp)

class VSin(Element):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.offset_v = 0.0
        self.amplitude_v = 0.0
        self.init_delay = 0.0
        self.frequency = 0.0
        self.damp_factor = 0.0
        self.phase = 0.0
    
    def read_spice(self, spice_line):
        pattern = r'^(?P<id>\w+)\s+(?P<n1>\w+)\s+(?P<n2>\w+)\s+(?P<type>\w+)(\s+)?\((?P<options>.+)\)$'
        match = re.match(pattern, spice_line)
        
        if match is None:
            raise SyntaxError("Match for VSIN failed")
        
        self.id = match.group('id')
        self.nodes = [match.group('n1'), match.group('n2'), "_I_" + self.id]
        self.time = 0.0
        
        options = re.split(r'\s|,', match.group('options'))
        options = [item for item in options if item != '']
        
        if len(options) != 6:
            raise SyntaxError(f"Expected 6 options, only {len(options)} received")
        
        options = [parse_number(item) for item in options]
        
        self.offset_v       = options[0]
        self.amplitude_v    = options[1]
        self.frequency      = options[2]
        self.init_delay     = options[3]
        self.damp_factor    = options[4]
        self.phase          = options[5]
        
    def stamp_dc(self):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.get_voltage(0)]
        ]
        return np.asarray(stamp)
    
    def stamp_ac(self, freq):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.amplitude_v]
        ]
        return np.asarray(stamp)
    
    def get_voltage(self, t):
        if t < self.init_delay:
            t_shift = 0
        else:        
            t_shift = t - self.init_delay
                
        exp_comp = np.exp(self.damp_factor * t_shift)
        sin_comp = np.sin((2 * math.pi * self.frequency * t_shift) + (self.phase * math.pi / 180))
        
        v = self.offset_v + (self.amplitude_v * sin_comp * exp_comp)
        return v
    
    def update_state(self, time, state_val_map):
        self.time = time
    
    def stamp_trans(self, h):
        stamp = [
            [0, 0, 1, 0],
            [0, 0, -1, 0],
            [1, -1, 0, self.get_voltage(self.time)]
        ]
        return np.asarray(stamp)

class VCCS(Element):
    def __init__(self):
        self.g = 0.0

    def read_spice(self, spice_line):
        inp = spice_line.split()
        inp = list(filter(None, inp))

        if len(inp) != 6:
            raise SyntaxError("Expected 6 arguments, only {len)inp) - 1} received")

        self.id     = inp[0]
        self.nodes  = [inp[1], inp[2], inp[3], inp[4]]
        self.g      = parse_number(inp[5])
        
    def stamp_dc(self):
        stamp = [
            [0, 0, self.g, -self.g, 0],
            [0, 0, -self.g, self.g, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        return np.asarray(stamp)

    def stamp_ac(self, freq):
        stamp = [
            [0, 0, self.g, -self.g, 0],
            [0, 0, -self.g, self.g, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        return np.asarray(stamp)

    def stamp_trans(self, h):
        stamp = [
            [0, 0, self.g, -self.g, 0],
            [0, 0, -self.g, self.g, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        return np.asarray(stamp)
