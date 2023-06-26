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

import numpy as np
import re
from collections import defaultdict

class Engine:
    def __init__(self):
        self.env        = None
        self.options    = {}
        self.print_nodes = []
        self.time       = 0
        self.data_dc    = None
        self.data_trans = None
        self.time_trans = None

    def set_env(self, inp_env):
        self.env = inp_env

    def run(self):
        ret = {}
        mode = self.options.get("mode", 0)
        if mode == 1:
            print("DC not implemented yet")
        elif mode == 2:
            self.run_trans(
                self.options.get("end_time", 0),
                self.options.get("step_size", 0)
            )
            ret = {"time": self.time_trans}
            for n in self.print_nodes:
                if n == "0":
                    ret[n] = np.zeros((self.data_trans.shape[0], 1))
                else:
                    ret[n] = [i[self.env.dict_node2idx[n] - 1] for i in self.data_trans]
        return ret

    def run_trans(self, end_time, step_size):
        timestamps = np.linspace(0, end_time, int(1 + end_time / step_size))

        self.data_trans = []
        self.time_trans = []

        soln = self.solve_dc()
        self.data_dc = soln
        self.env.set_node_vals(soln)
        self.env.update_comp_states(0)
        self.data_trans.append(soln)
        self.time_trans.append(0)
        # self.data_trans = np.vstack((self.data_trans, soln))

        for t in timestamps[1:]:
            soln = self.solve_trans_step(step_size)
            self.env.set_node_vals(soln)
            self.env.update_comp_states(t)
            # self.data_trans = np.vstack((self.data_trans, soln))
            self.data_trans.append(soln)
            self.time_trans.append(t)

        self.data_trans = np.column_stack((self.data_trans, timestamps))

    def solve_trans_step(self, step_size):
        mat = self.env.get_mat_trans(step_size)
        lhs_mat = mat[:, :-1]
        rhs_vec = mat[:,-1]

        soln_vec = np.linalg.solve(lhs_mat, rhs_vec)
        return soln_vec

    def solve_dc(self):
        mat = self.env.get_mat_dc()
        lhs_mat = mat[:, :-1]
        rhs_vec = mat[:,-1]

        print(lhs_mat)
        print(rhs_vec)

        soln_vec = np.linalg.solve(lhs_mat, rhs_vec)
        return soln_vec

    def add_option(self, opt_key, opt_val):
        self.options[opt_key] = opt_val

    def add_node_print(self, node_identifier):
        pattern = r'^(v|i|V|I)\((\w+)\)$'

        # Check if the input string matches the pattern
        tokens = re.match(pattern, node_identifier)

        if tokens is not None:
            # Extract the matching group
            x = tokens.group(2)
            t = tokens.group(1).lower()
            if t == 'v':
                node = x
            elif t == 'i':
                node = "_I_" + x
            if node in self.env.dict_node2idx.keys():
                self.print_nodes.append(node)
        else:
            print('Input string does not match the pattern V(x) or I(x).')
