"""
@Author: Joris van Vugt, Moira Berens, Leonieke van den Bulk

Entry point for the creation of the variable elimination algorithm in Python 3.
Code to read in Bayesian Networks has been provided. We assume you have installed the pandas package.

"""
from read_bayesnet import BayesNet
from variable_elim import VariableElimination

if __name__ == '__main__':
    # The class BayesNet represents a Bayesian network from a .bif file in several variables
    net = BayesNet('earthquake.bif')  # Format and other networks can be found on http://www.bnlearn.com/bnrepository/
    # These are the variables read from the network that should be used for variable elimination
    # print("Nodes:")
    # print(net.nodes)
    # print("Values:")
    # print(net.values)
    # print("Parents:")
    # print(net.parents)
    # print("Probabilities:")
    # print(net.probabilities)

    # Make your variable elimination code in the separate file: 'variable_elim'.
    # You use this file as follows:
    ve = VariableElimination(net)

    # Set the node to be queried as follows:
    query = 'MaryCalls'

    # The evidence is represented in the following way (can also be empty when there is no evidence):
    evidence = {'Burglary': 'False', 'Earthquake': 'True'}

    # Determine your elimination ordering before you call the run function. The elimination ordering
    # is either specified by a list or a heuristic function that determines the elimination ordering
    # given the network. Experimentation with different heuristics will earn bonus points. The elimination
    # ordering can for example be set as follows:
    no_children_nodes = []
    no_parents_nodes = []

    for node in net.nodes:
        if not any(node in parents for parents in net.parents.values()):
            no_children_nodes.append(node)
        if not net.parents.get(node):
            no_parents_nodes.append(node)

    rest_of_nodes = list(set(net.nodes) - set(no_children_nodes) - set(no_parents_nodes))

    order = no_children_nodes + no_parents_nodes + rest_of_nodes
    order.remove(query)
    print("Elimination order:")
    print(order)
    print()

    elim_order = order

    # Call the variable elimination function for the queried node given the evidence and the elimination ordering as
    # follows:
    ve.run(query, evidence, elim_order)
