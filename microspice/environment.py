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

import copy
import numpy as np

class Environment:
    def __init__(self):
        self.num_nodes      = 1             # Total number of nodes

        self.dict_id2comp   = {}            # Map from component ID to component object
        self.dict_node2idx  = {"0": 0}      # Map from node name to node index
        self.dict_node2val  = {"0": 0}      # Map from node name to node value
        self.dict_comp2node = {}            # Map from component ID to nodes connected to the component

    # Add a component to the enviornment
    def add_component(self, comp):
        self.dict_id2comp[comp.id] = comp                   # Add to the component dictionary

        node_idx_ls = []                                    # Maintain a list of nodes connected with the component

        for node in comp.nodes:
            # Add a new node into the enviornment node dictionary
            if node not in self.dict_node2idx:
                self.dict_node2idx[node] = self.num_nodes
                self.num_nodes += 1
            node_idx_ls.append(self.dict_node2idx[node])    # Adding nodes connected to the component
        
        self.dict_comp2node[comp.id] = node_idx_ls          # Add nodes to the component to node dictionary

    # Get the DC matrix to solve
    def get_mat_dc(self):
        stamp_mat = np.zeros((self.num_nodes, self.num_nodes + 1))

        components = self.dict_id2comp.values()
        
        for comp in components:
            idx_vec = self.dict_comp2node[comp.id]
            stamp = comp.stamp_dc()

            # "Stamping"
            for j, idx in enumerate(idx_vec):
                stamp_mat[idx, [idx_vec + [self.num_nodes]]] += stamp[j, :]

        mat = stamp_mat[1:, 1:]
        return mat

    def get_mat_trans(self, step_size):
        stamp_mat = np.zeros((self.num_nodes, self.num_nodes + 1))

        components = self.dict_id2comp.values()
        for comp in components:
            idx_vec = self.dict_comp2node[comp.id]
            stamp   = comp.stamp_trans(step_size)

            # "Stamping" the matrix
            for j, idx in enumerate(idx_vec):
                stamp_mat[idx, [idx_vec + [self.num_nodes]]] += stamp[j, :]

        mat = stamp_mat[1:, 1:]
        return mat

    def set_node_vals(self, soln_vec):
        for node in self.dict_node2idx.keys():
            if node != "0":
                self.dict_node2val[node] = soln_vec[self.dict_node2idx[node] - 1]

    def update_comp_states(self, time):
        components = self.dict_id2comp.values()
        for comp in components:
            comp.update_state(time, self.dict_node2val)

    def copy_element(self):
        cp = Environment()
        for comp in self.dict_id2comp.values():
            cp.add_component(copy.copy(comp))
        return cp
