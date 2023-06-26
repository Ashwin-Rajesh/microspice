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

import microspice.parser        as parser
import microspice.error.error   as error
import matplotlib.pyplot        as plt

class Microspice():
    def __init__(self) -> None:
        self.parser     = parser.Parser()
        self.run_num    = 0        

    def parse_file(self, file_name):
        ret = self.parser.read(file_name)
        if(ret.level()):
            print(ret.to_str())
            return ret
        
        ret = self.parser.parse()
        if(ret.level()):
            print(ret.to_str())
            return ret
        
        self.run_num    = 0        
        return ret
    
    def parse_and_run_file(self, file_name):
        self.parse_file(file_name)
        
        while(not self.done()):
            self.run_next()
            self.disp_result()

        print("Finished all runs")
    
    def done(self):
        return self.run_num >= len(self.parser.envs)

    def run_next(self):
        if(self.done()):
            return error.GenError("Simulated all environments")
        
        self.parser.eng.set_env(self.parser.envs[self.run_num])
        self.result     = self.parser.eng.run()
        self.run_num   += 1

        return error.OkError()

    def disp_result(self):
        plt.title(f'Transient simulation result {self.run_num}')
        plt.ylabel('Voltage (V)')
        plt.xlabel('Time (s)')

        for o in self.result.keys():
            if o != "time":
                data = self.result[o]
                plt.plot(self.result["time"], data, label="V(" + o + ")")
                print("V(" + o + "):", data[0])

        plt.legend()
        plt.show()

    def reset(self):
        self.parser = parser.Parser()
