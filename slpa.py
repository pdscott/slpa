# slpa.py
# Author: Preston Scott pdscott2
# CSC 591
# Given an edgelist, this script builds the graph, then performs overlapping
# community identification using the Speaker-listener Label Propagation Algorithm
# (SLPA)

import random
import sys

################################################################################
# Node object for building graph with embedded method for sending labals and
# embedded memory of labels passed to it.
################################################################################
class Node:
    # Initializes a new node
    # label: the id of the node
    # memory: dictionary of labels seen by this node.
    # memory_count: total number of labels passed to this node
    def __init__(self, label):
        self.label = label
        self.memory = dict()
        self.memory[label] = 1
        self.memory_count = 1

    # Randomly selects a label with probability proportional to the occurrence 
    # frequency of this label in its memory and sends the selected label to 
    # the listener.
    # Retuns: chosen label
    def send(self):
        sum = 0.0
        r = random.random()
        keys = self.memory.keys()
        for key in keys:
            sum = sum + float(self.memory[key]) / float(self.memory_count)
            if sum >= r:
                return key

################################################################################
# Graph object for building graph with embedded properties for node lists, edge
# lists, and identified communities
################################################################################
class Graph():
    # Initializes a new graph
    # node_list: dictionary where keys are node labels and values are node objects
    # edge_list: dictionary where keys are node labels and values are lists of 
    #            edge connected neighbors.
    # community_list: dictionary where keys are community ids and values are sets
    #                 of nodes in that community.
    def __init__(self):
        self.node_list = dict()
        self.edge_list = dict()
        self.community_list = dict()

    # Add a node to the graph
    # label: id of the node
    def add_node(self, label):
        node = Node(label)
        self.node_list[label] = node
        self.edge_list[label] = []

    # Return a list of all nodes in the graph
    def get_nodes(self):
        return self.edge_list.keys()

    # Add an edge to the graph. Adds endpoints as nodes if there are not present
    # src: the source node for the edge
    # dst: the destination node for the edge
    def add_edge(self, src, dst):
        if not self.edge_list.has_key(src):
            self.add_node(src)
        if not self.edge_list.has_key(dst):
            self.add_node(dst)
        self.edge_list[src].append(dst)
        self.edge_list[dst].append(src)

    # Return a list of all edges in the graph 
    # Format: [[1,2],[3,4], etc]
    def get_edges(self):
        edges = []
        for src in self.edge_list.keys():
            dst_list = self.edge_list[src]
            for dst in dst_list:
                edge = [src, dst]
                edges.append(edge)
        return edges

    # Return a list of all neighbors for the given node
    # node: node of interest 
    def get_neighbors(self, node):
        return self.edge_list[node]

    # print the edgelist for the graph
    def print_graph(self):
        for node, neighbors in self.edge_list.items():
            print(node, neighbors)

    # print the current state of the memory for each node
    def print_memory(self):
        for node in self.node_list.values():
            print node.label, node.memory

    # write all identified communities to file
    # filename: output file to write to
    def print_communities(self, filename):
        file = open(filename, 'w')
        for key in self.community_list.keys():
            file.write('%s\n' % sorted(self.community_list[key]))
        file.close()
        num_comms = len(self.community_list.keys())
        print '%s different communities identified and written to %s' % (num_comms, filename)

    # read an edgelist from an input file and build a graph (self)
    # filename: input file to read from
    def import_edges(self, filename):
        file = open(filename,'r')
        
        # throw the fist line away
        file.readline()

        for line in file:
            words = line.split(' ')
            src = int(words[0].strip())
            dst = int(words[1].strip())
            self.add_edge(src, dst)
        file.close()


################################################################################
# SLPA object for holding the graph data structure and running the SLPA
# algorithm
################################################################################            
class SLPA():
    # initialize a new object
    # filename: input file to read from
    # num_iterations: numner of times to run the label propagation
    # threshold: float from 0 to 0.5 specifying a lower probability bound for 
    # accepting community membership
    def __init__(self, filename, num_iterations, threshold):
        self.graph = Graph()
        self.graph.import_edges(filename)
        self.num_iterations = num_iterations
        self.threshold = threshold

    # run the algorithm based on the parameters given to the object during 
    # initialization
    def run(self):
        nodes = self.graph.node_list.keys()
        sys.stdout.write('[')
        for i in range(self.num_iterations):
            sys.stdout.write('=')
            sys.stdout.flush()
            random.shuffle(nodes)
            self.propagate(nodes)
        print('] Label Propagation Complete')
        self.post_process()      
            
    # perform propagation of labels with each node serving as listener in a 
    # random order.
    # random nodes: list of nodes in random order
    def propagate(self, random_nodes):
        for random_node in random_nodes:
            messages = dict()
            most_popular_message = -1
            listener = self.graph.node_list[random_node]
            neighbors = self.graph.edge_list[random_node]

            #Poll each neighbor one-by-one and save receipts in messages dict
            for neighbor in neighbors:
                sender = self.graph.node_list[neighbor]
                message = sender.send()

                if not messages.has_key(message):
                    messages[message] = 1
                else:
                    messages[message] += 1
                if messages[message] > most_popular_message:
                    most_popular_message = message

            # Write the most common message received to listener memory
            if not most_popular_message == -1:
                if not listener.memory.has_key(most_popular_message):
                    listener.memory[most_popular_message] = 1
                    listener.memory_count += 1
                else:
                    listener.memory[most_popular_message] += 1
                    listener.memory_count += 1
    
    # Scrap all received labels with probability density less than threshold
    # Then pick out communities and save to community list
    def post_process(self):
        for node in self.graph.node_list.values():
            for key in node.memory.keys():
                probability = float(node.memory[key]) / float(node.memory_count)
                if probability < self.threshold:
                    node.memory.pop(key, None)
        for node in self.graph.node_list.values():
            for key in node.memory.keys():
                if not self.graph.community_list.has_key(key):
                    self.graph.community_list[key] = set()
                    self.graph.community_list[key].add(node.label)
                else:
                    self.graph.community_list[key].add(node.label)

# Initiates the program
# USAGE: python slpa [filename] [num_iterations] [threshold]
# filename: existing file containing edgelist (space separated endpoints)
# num_iterations: number of iterations for the SLPA label proopagation
# threshold: minimum probability density for community membership             
def main():
    if len(sys.argv) == 2 and sys.argv[1] == '-h':
        print
        print "USAGE: python slpa.py ['input file'] ['output file'] [num_iterations] [threshold]"
        print 'filename: existing file containing edgelist (space separated endpoints)'
        print 'num_iterations: number of iterations for the SLPA label proopagation e.g. 20'
        print 'threshold: minimum probability density for community membership e.g. 0 - 0.5'
        print
        sys.exit()

    if not len(sys.argv) == 5:
        print "USAGE: python slpa.py ['input file'] ['output file'] [num_iterations] [threshold]"
        print 'for help, type python slpa.py -h'
        sys.exit()
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    num_iterations = int(sys.argv[3])
    threshold = float(sys.argv[4])
 
    slpa = SLPA(in_file, num_iterations, threshold)
    slpa.run()
    slpa.graph.print_communities(out_file)

if __name__ == "__main__":
    main()