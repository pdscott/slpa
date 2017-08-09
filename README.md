# slpa
Implementation of Speaker-Listener Label Propagation Algorithm (SLPA)

Note: This is an implementation of the SLPA algorithm described in “Towards Linear Time Overlapping Community Detection in Social Networks” by Xie and Szymanski.

Required software:
Python 2.7
imported modules: random, sys

Environmental variables:
None

Instructions for running:
```python 
python slpa.py ['input file'] ['output file'] [num_iterations] [threshold]
 ```
Example: 
```python
python slpa.py 'edgelist.txt' 'communities.txt' 20 0.5
```
For help, type: 
```python
python slpa.py -h
```
NOTE: The edglist reader automatically skips the first line of the file since many input
graphs contain node and edge sums as the first line.

Results Interpretation:
    Each identified community is printed as a set of nodes on a separate line in the specified output file.

Sample input and output files:
	test.txt - contains a nine node graph for testing
	communities_test.txt - output file generated after running "python slpa.py 'edgelist.txt' 'communities.txt' 20 0.5"
	                     - the file contains two lines representing the two identified communities
	                     - each line contains the nodes in that community



