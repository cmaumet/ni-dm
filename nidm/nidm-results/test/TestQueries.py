#!/usr/bin/env python
'''Test that NIDM-Results queries are functional 

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
import unittest
from rdflib.graph import Graph
from nidmresults.test.test_commons import *
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

RELPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestQueries(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestQueries, self).__init__(*args, **kwargs)    
        self.examples = dict()
        for example_file in import_test_filenames:
            ttl_file = os.path.join(os.path.dirname(os.path.dirname(
                                os.path.abspath(__file__))), example_file)
            # ttl_file_url = get_turtle(provn_file)
            # ttl_file = provn_file.replace(".provn", ".ttl")

            # Read turtle
            self.examples[example_file] = Graph()
            self.examples[example_file].parse(ttl_file, format='turtle')

    def test_get_contrasts(self):
        logger.info("TestQueries: test_get_contrasts")
        self.run_query_and_test("get_contrasts.rq", "Contrast not found", "Contrast query")
        
    def test_get_height_extent_metadata(self):
        self.run_query_and_test("height_extent_metadata.rq", "Height/Extent metatdata not found", "Height/Extent query")

    def test_peaks(self):
        self.run_query_and_test("peak.rq","Peaks not found","Peaks query")
        
    def test_clusters(self):
        self.run_query_and_test("cluster.rq","Clusters not found","Clusters query")
            
    def test_get_mask(self):
        logger.info("TestQueries: test_get_mask")
        self.run_query_and_test("get_mask.rq", "Mask not found", "Mask query")        

    def run_query_and_test(self, query_file, error_prefix, query_result_prefix):
        my_exception = dict()

        file = open(os.path.join(RELPATH, 'query', query_file), 'r')
        query = file.read();
        
        my_exception = dict()

        for example_name, example_graph in self.examples.items():
            exception_msg = dict()
            sd = example_graph.query(query)

            if not sd:
                key = error_prefix
                if not key in my_exception:
                    my_exception[key] = set([example_name])
                else:
                    my_exception[key].add(example_name)

                my_exception = merge_exception_dict(my_exception, exception_msg)
            else:
                for row in sd:
                    logger.info(example_name+"\t\t"+query_result_prefix+":")
                    logger.info(row)

        # Aggregate errors over examples for conciseness
        if my_exception:
            error_msg = ""
            for unrecognised_class_name, examples in my_exception.items():
                error_msg += unrecognised_class_name+" (from "+', '.join(examples)+")"
            raise Exception(error_msg)

if __name__ == '__main__':
    unittest.main()
