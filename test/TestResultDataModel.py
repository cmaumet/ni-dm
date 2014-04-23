#!/usr/bin/env python
'''Common tests across-software for NI-DM export. 
The software-specific test classes must inherit from this class.

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
import unittest
import os, inspect
from subprocess import call
import re
import rdflib
from rdflib.graph import Graph

import logging

logger = logging.getLogger(__name__)


def get_readable_name(graph, item):
    # Look for label
    name = graph.label(item)
    # Look for name without path
    if not name:
        name = os.path.basename(item)
        # Keep full path
        if not name:
            name = item
    return name

def get_alternatives(graph,s=None,p=None, o=None):
    found = ""
    
    for (s_in,  p_in, o_in) in graph.triples((s,  p, o)):
        if not o:  
            found += "; "+get_readable_name(graph, o_in)
        if not p:  
            found += "; "+get_readable_name(graph, p_in)
    if len(found) > 100:
        found = '<many alternatives>'
    else:
        found = found[2:]
    return found

# FIXME: Extend tests to more than one dataset (group analysis, ...)
'''Tests based on the analysis of single-subject auditory data based on test01_spm_batch.m using SPM12b r5918.

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
class TestResultDataModel(object):
    def setUp(self):
        self.my_execption = ""

        # Display log messages in console
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        # Current script directory is test directory (containing test data)
        self.test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    '''Print the results query 'res' to the console'''
    def print_results(self, res):
        for idx, row in enumerate(res.bindings):
            rowfmt = []
            print "Item %d" % idx
            for key, val in sorted(row.items()):
                rowfmt.append('%s-->%s' % (key, val.decode()))
            print '\n'.join(rowfmt)

    '''Check if the results query 'res' contains a value for each field'''
    def successful_retreive(self, res, info_str=""):
        if not res.bindings:
            self.my_execption = info_str+""": Empty query results"""
            return False
        for idx, row in enumerate(res.bindings):
            rowfmt = []
            for key, val in sorted(row.items()):
                logging.debug('%s-->%s' % (key, val.decode()))
                if not val.decode():
                    self.my_execption += "\nMissing: \t %s" % (key)
                    return False
        return True

        if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
            raise Exception(self.my_execption)


    ''' Compare gt_graph and other_graph '''
    def compare_full_graphs(self, gt_graph, other_graph):
        # Check for predicates which are not in common to both graphs (XOR)
        diff_graph = gt_graph ^ other_graph

        # FIXME: There is probably something better than using os.path.basename to remove namespaces
        exlude_s = list()
        missing_s = list()

        exc_wrong = ""
        exc_added = ""
        exc_missing = ""

        for s,p,o in diff_graph.triples( (None,  None, None) ):
            # If triple is found in other_graph
            if (s,  p, o) in other_graph:
                # If subject and predicate found in gt_graph, then object is wrong
                if (s,  p, None) in gt_graph:
                    exc_wrong += "\nWrong o:\t'%s' on '%s' should be '%s' (instead of '%s'?)"%(get_readable_name(other_graph, p),get_readable_name(other_graph, s),get_alternatives(gt_graph,s=s,p=p),get_readable_name(other_graph, o))
                # If subject and object found in gt_graph, then predicate is wrong
                elif (s,  None, o) in gt_graph:
                    exc_wrong += "\nWrong p:\tBetween '%s' \tand '%s' \tshould be '%s' (instead of '%s'?)"%(get_readable_name(other_graph,s),get_readable_name(other_graph,o),get_readable_name(other_graph,p),get_alternatives(gt_graph,s=s,o=o))
                # If predicate and object found in gt_graph, then subject is wrong
                elif (None,  p, o) in gt_graph:
                    if not (s, None, None) in gt_graph:
                        if not s in exlude_s:
                            exc_added += "\nAdded:\t'%s'"%(s)
                            exlude_s.append(s)
                    else:
                        found_subject = ""
                        for (s_gt_graph,  p_gt_graph, o_gt_graph) in gt_graph.triples((None,  p, o)):
                            found_subject += "; "+os.path.basename(s_gt_graph)
                        if len(found_subject) > 20:
                            found_subject = 'many alternatives'
                        else:
                            found_subject = "'"+found_subject[2:]+"'?"
                        exc_wrong += "\nWrong s:\t'%s' \tto '%s' \tis '%s' (instead of %s)."%(os.path.basename(p),get_readable_name(other_graph, o),os.path.basename(s),found_subject)
                # If only subject found in gt_graph
                elif (s,  None, None) in gt_graph:
                    # gt_graph_possible_value = ""
                    # for (s_gt_graph,  p_gt_graph, o_gt_graph) in gt_graph.triples((s,  p, None)):
                    #     gt_graph_possible_value += "; "+os.path.basename(p_gt_graph)
                    exc_added += "\nAdded:\tin '%s', '%s' \t ('%s')."%(other_graph.label(s),os.path.basename(p),os.path.basename(o))
                # If subject is *not* found in gt_graph
                else:
                    if not s in exlude_s:
                        exc_added += "\nAdded:\t'%s'"%(s)
                        exlude_s.append(s)
            # If subject and predicate are found in gt_graph 
            elif (s,  p, o) in gt_graph:
                # If subject and predicate found in other_graph
                if (s,  p, None) in other_graph:
                    # Do nothing as already taken into account before
                    a = 1
                # If subject found in other_graph
                elif (s,  None, None) in other_graph:
                    other_graph_possible_value = ""
                    for (s_export,  p_export, o_export) in other_graph.triples((s,  None, None)):
                        other_graph_possible_value += "; "+os.path.basename(p_export)
                    exc_missing += "\nMissing:\t'%s' \ton '%s'"%(os.path.basename(p),gt_graph.label(s))
                # If subject is *not* found in other_graph
                else:
                    if not s in missing_s:
                        exc_missing += "\nMissing:\t'%s' "%(s)
                        missing_s.append(s)

        self.my_execption += exc_wrong+exc_added+exc_missing