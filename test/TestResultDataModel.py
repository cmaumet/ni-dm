#!/usr/bin/env python
'''Common tests across-software for NI-DM export. 
The software-specific test classes must inherit from this class.

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
import unittest
import os
from subprocess import call
import re
import rdflib
from rdflib.graph import Graph

import logging

logger = logging.getLogger(__name__)

# FIXME: Extend tests to more than one dataset (group analysis, ...)
'''Tests based on the analysis of single-subject auditory data based on test01_spm_batch.m using SPM12b r5918.

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
class TestResultsDataModel(object):

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
                # If subject and predicate found in gt_graph
                if (s,  p, None) in gt_graph:
                    gt_graph_possible_value = ""
                    for (s_gt_graph,  p_gt_graph, o_gt_graph) in gt_graph.triples((s,  p, None)):
                        gt_graph_possible_value += "; "+os.path.basename(o_gt_graph)
                    exc_wrong += "\nWrong:   '%s' \ton '%s' \tis '%s' (instead of '%s')"%(os.path.basename(p),other_graph.label(s),os.path.basename(o),gt_graph_possible_value[2:])
                # If subject found in gt_graph
                elif (s,  None, None) in gt_graph:
                    gt_graph_possible_value = ""
                    for (s_gt_graph,  p_gt_graph, o_gt_graph) in gt_graph.triples((s,  p, None)):
                        gt_graph_possible_value += "; "+os.path.basename(p_gt_graph)
                    exc_added += "\nAdded:   '%s' \ton '%s' (instead of '%s')"%(os.path.basename(p),other_graph.label(s),gt_graph_possible_value[2:])
                # If subject is *not* found in gt_graph
                else:
                    if not s in exlude_s:
                        exc_added += "\nAdded:   '%s'"%(s)
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
                    for (s_export,  p_export, o_export) in other_graph.triples((s,  p, None)):
                        other_graph_possible_value += "; "+os.path.basename(p_export)
                    exc_missing += "\nMissing:   '%s' \ton '%s' (instead of '%s')"%(os.path.basename(p),gt_graph.label(s),other_graph_possible_value[2:])
                # If subject is *not* found in other_graph
                else:
                    if not s in missing_s:
                        exc_missing += "\nMissing:   '%s' "%(s)
                        missing_s.append(s)

        self.my_execption += exc_wrong+exc_added+exc_missing