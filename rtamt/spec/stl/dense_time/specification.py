from antlr4 import *
from antlr4.InputStream import InputStream

from rtamt.parser.stl.StlLexer import StlLexer
from rtamt.parser.stl.StlParser import StlParser
from rtamt.spec.stl.discrete_time.specification_parser import STLSpecificationParser

from rtamt.parser.stl.error.parser_error_listener import STLParserErrorListener
from rtamt.exception.stl.exception import STLParseException

from rtamt.spec.stl.discrete_time.pastifier import STLPastifier

from rtamt.spec.stl.discrete_time.specification import STLDiscreteTimeSpecification
from rtamt.evaluator.stl.online_evaluator import STLOnlineEvaluator
from rtamt.evaluator.stl.offline_evaluator import STLOfflineEvaluator
from rtamt.spec.stl.dense_time.specification_parser import STLDenseTimeSpecificationParser

from rtamt.enumerations.options import TimeInterpretation

class STLDenseTimeSpecification(STLDiscreteTimeSpecification):
    """A class used as a container for STL continuous time specifications
       Inherits STLSpecification

    Attributes:

    """
    def __init__(self,is_pure_python=True):
        """Constructor for STL Specification"""
        super(STLDenseTimeSpecification, self).__init__(is_pure_python)
        self.visitor = STLDenseTimeSpecificationParser(self)
        self.time_interpretation = TimeInterpretation.DENSE


    def parse(self):
        if self.spec is None:
            raise STLParseException('STL specification if empty')

        # Parse the STL spec - ANTLR4 magic

        entire_spec = self.modular_spec + self.spec
        input_stream = InputStream(entire_spec)
        lexer = StlLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = StlParser(stream)
        parser._listeners = [STLParserErrorListener()]
        ctx = parser.stlfile()

        # Create the visitor for the actual spec nodes
        visitor = STLSpecificationParser(self)
        self.top = visitor.visitStlfile(ctx)

        # Translate bounded future STL to past STL
        pastifier = STLPastifier(self.is_pure_python)
        self.top.accept(pastifier)
        past = pastifier.pastify(self.top)
        self.top = past

        # Initialize the online_evaluator
        self.online_evaluator = STLOnlineEvaluator(self)
        self.offline_evaluator = STLOfflineEvaluator(self)
        self.top.accept(self.online_evaluator)

    # Online
    def update(self, *args, **kargs):
        # list_inputs:
        # example [['p', [[1.1, 2.2], [1.3, 2.5], [1.7, 2]]], ['q', [[1, 2], [1.5, 3.5]]]
        for arg in args:
            var_name = arg[0]
            var_object = arg[1]
            self.var_object_dict[var_name] = var_object
        out = self.online_evaluator.evaluate(self.top, [])
        self.var_object_dict = self.var_object_dict.fromkeys(self.var_object_dict, [])
        return out

    # def update_final(self, *args, **kargs):
    #     for arg in args:
    #         var_name = arg[0]
    #         var_object = arg[1]
    #         self.var_object_dict[var_name] = var_object
    #     out = self.evaluator.evaluate(self.top, ['final'])
    #     self.var_object_dict = self.var_object_dict.fromkeys(self.var_object_dict, [])
    #     return out

    # Offline
    def evaluate(self, *args, **kargs):
         for arg in args:
             var_name = arg[0]
             var_object = arg[1]
             self.var_object_dict[var_name] = var_object
         out = self.offline_evaluator.evaluate(self.top, [])
         self.var_object_dict = self.var_object_dict.fromkeys(self.var_object_dict, [])
         return out







