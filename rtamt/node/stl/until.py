from rtamt.node.stl.binary_node import BinaryNode

class Until(BinaryNode):
    """
    A class for storing STL Since nodes
    Inherits TemporalNode
    """
    def __init__(self, child1, child2, bound=None, is_pure_python=True):
        """Constructor for Until node

            Parameters:
                child1 : stl.Node
                child2 : stl.Node
                bound : Interval
        """
        super(Until, self).__init__(child1, child2, bound)
        self.bound = bound

        self.name = '(' + child1.name + ')until[' + str(bound.begin) + ',' + str(
            bound.end) + '](' + child2.name + ')'

        self.in_vars = child1.in_vars + child2.in_vars
        self.out_vars = child1.out_vars + child2.out_vars

