# Mini spice engine

This is a small spice parser and engine written in python that runs AC, DC and transient simulations for linear elements. 

This demonstrates the bare basics of a SPICE engine. It is built with modularity, extensibility and simplicity in mind rather than runtime performace.

The project was first implemented in MATLAB as part of the *"CAD for high speed circuits"* course by Prof. Dipanjan Gope at IISc, Bangalore (Spring 2023) and then converted to python with the help of ChatGPT.

---

## Index

- ```examples``` : Example spice netlists
- ```docs```  : Code documentation
- ```microspice``` : Python source files
  - ```elements.py``` : Different elements supported in microspice
  - ```environment.py``` : The environment contains the components and connectivity information of a spice netlist
  - ```engine.py``` : The spice solver. Also handles different modes and simulation options
  - ```microspice.py``` : Toplevel interface for using microspice
  - ```parser.py``` : Parses the spice netlist
  - ```utils.py``` : Common utilities like unit and type conversion
  - ```error``` : Error handling functionality
- ```microspice_matlab``` : The original matlab implementation (for reference)
- ```run.ipynb``` : Example jupyter notebook to run microspice on the sample spice files 
