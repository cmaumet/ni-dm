# For each document in the NIDM repository, this script checks if there is a public document with the same content (from title)
# in the Prov Store (https://provenance.ecs.soton.ac.uk/store). If there is none, the document is uploaded and its README file is updated
# to link to the json, turtle, svg, PDF and png serialisations. 

# To use this script you need to have an account on the Prov Store (cf. https://provenance.ecs.soton.ac.uk/store/account/signup/) and to
# create a file named store_login_key.txt in the same directory including the following text: "mylogin:mykey" where mylogin 
# must be replaced by your Prov Store login and mykey by your ApiKey (cf. https://provenance.ecs.soton.ac.uk/store/account/developer/)

import urllib2
import json
import logging
import os
import rdflib
from rdflib.graph import Graph
from rdflib.compare import *
import sys

RELPATH = os.path.dirname(os.path.abspath(__file__))
NIDMRESULTSPATH = os.path.dirname(RELPATH)

# Append test directory to path
sys.path.append(os.path.join(RELPATH, "..", "test"))
from TestCommons import example_filenames
from CheckConsistency import *
from OwlReader import OwlReader

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class_termsPATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'terms')

CURATION_COLORS = dict()
CURATION_COLORS[OBO_PENDING_FINAL] = "green"
CURATION_COLORS[OBO_METADATA_COMPLETE] = "orange"
CURATION_COLORS[OBO_METADATA_INCOMPLETE] = "orange"
CURATION_COLORS[OBO_REQUIRES_DISCUSSION] = "orange"
CURATION_COLORS[OBO_UNCURATED] = "red"
CURATION_COLORS[OBO_TO_BE_REPLACED] = "yellow"

CURATION_LEGEND = dict()
CURATION_LEGEND["green"] = "Pending final vetting"
CURATION_LEGEND["orange"] = "Metadata incomplete; Metadata complete; Requires discussion"
CURATION_LEGEND["red"] = "Uncurated"
CURATION_LEGEND["yellow"] = "To be replaced with external ontology term"

CURATION_ORDER = list([OBO_PENDING_FINAL, OBO_METADATA_INCOMPLETE, OBO_REQUIRES_DISCUSSION, OBO_UNCURATED, OBO_TO_BE_REPLACED])

class UpdateTermReadme():

    def __init__(self, owl_file):
        self.owl = OwlReader(owl_file)

    # Write out Readme
    def write_readme(self, readme_file, readme_txt):
        readme_file_open = open(readme_file, 'w')
        readme_file_open.write(readme_txt)
        readme_file_open.close()

    def create_term_row(self, term_name, definition, same_as, editor, color, 
        range_value=None, domain=None):
        img_color = ""        
        if color:
            img_color = '<img src="../../../doc/content/specs/img/'+color+'.png?raw=true"/>  ' 

        if same_as:
            same_as = "(same as: <a href="+same_as+">"+same_as+"</a>)"

        range_domain = ""
        if range_value is not None:
            range_domain = """
    <td>"""+domain+"""</td>
    <td>"""+range_value+"""</td>"""

        term_row = """
<tr>
    <td>"""+img_color+"""</td>
    <td><b>"""+term_name+""": </b>"""+definition+same_as+editor+"""</td>"""+range_domain+"""
</tr>"""
        return term_row

    def create_curation_legend(self, order):
        curation_legend = "<b>Curation status</b>: \n"
        curation_colors_sorted = [(key, CURATION_COLORS.get(key)) for key in order]

        covered_colors = list()
        for curation_color in curation_colors_sorted:
            # curation_status =  str(self.owl.qname(curation_color[0]))
            # curation_status_labels = self.owl.objects(curation_color[0], RDFS['label'])
            # curation_status = ", ".join(list(curation_status_labels))

            color =  curation_color[1]
            if not color in covered_colors:
                curation_legend = curation_legend+'<img src="../../../doc/content/specs/img/'+color+'.png?raw=true"/>&nbsp;'+\
                    CURATION_LEGEND[color]+";\n"
                covered_colors.append(color)
        return curation_legend

    # Get README text according to owl file information
    def update_readme(self, readme_file): 
        class_terms = dict()
        prpty_terms = dict()
        definitions = dict()
        editors = dict()
        ranges = dict()
        domains = dict()
        sameas = dict()

        for owl_term in self.owl.classes.union(self.owl.properties):
            curation_status = self.owl.get_curation_status(owl_term)
            definition = self.owl.get_definition(owl_term)
            editor = self.owl.get_editor(owl_term)
            range_value = self.owl.get_range(owl_term)
            domain = self.owl.get_domain(owl_term)
            same = self.owl.get_same_as(owl_term)
            
            if definition:
                if curation_status:
                    curation_key = curation_status
                    term_key = self.owl.graph.qname(owl_term)
                    if owl_term in self.owl.classes:
                        class_terms.setdefault(curation_key, list()).append(term_key)
                    else:
                        if owl_term in self.owl.properties:
                            prpty_terms.setdefault(curation_key, list()).append(term_key)
                    definitions[term_key] = definition
                    editors[term_key] = editor
                    ranges[term_key] = range_value
                    domains[term_key] = domain
                    sameas[term_key] = same


        # Include missing keys and do not display ready for release terms
        order=CURATION_ORDER+(list(set(class_terms.keys()).union(set(prpty_terms.keys())) - set(CURATION_ORDER+list([OBO_READY]))))
        class_terms_sorted = [(key, class_terms.get(key)) for key in order]
        prpty_terms_sorted = [(key, prpty_terms.get(key)) for key in order]

        class_table_txt = "<h2>Classes</h2>\n<table>\n<tr><th>Curation Status</th><th>Term</th></tr>"
        for tuple_status_term in class_terms_sorted:
            curation_status = tuple_status_term[0]
            class_names = tuple_status_term[1]

            if class_names:
                for class_name in sorted(class_names):
                    class_table_txt += self.create_term_row(class_name, \
                        definitions[class_name], \
                        sameas[class_name], \
                        editors[class_name], \
                        CURATION_COLORS.setdefault(curation_status, ""))
        class_table_txt = class_table_txt+"\n</table>"

        prpty_table_txt = "<h2>Properties</h2>\n<table>\n<tr><th>Curation Status</th><th>Term</th><th>Domain</th><th>Range</th></tr>"
        for tuple_status_term in prpty_terms_sorted:
            curation_status = tuple_status_term[0]
            term_names = tuple_status_term[1]

            if term_names:
                for term_name in sorted(term_names):
                    prpty_table_txt += self.create_term_row(term_name, \
                        definitions[term_name], \
                        sameas[term_name], \
                        editors[term_name], \
                        CURATION_COLORS.setdefault(curation_status, ""), \
                        ranges[term_name], \
                        domains[term_name])
        prpty_table_txt = prpty_table_txt+"\n</table>"

        curation_legend = self.create_curation_legend(order)
        title = "<h1>NIDM-Results Terms curation status</h1>"
        self.write_readme(readme_file, title+curation_legend+class_table_txt+prpty_table_txt)

if __name__ == '__main__':
    # Retreive owl file for NIDM-Results
    owl_file = os.path.join(class_termsPATH, 'nidm-results.owl')

    # check the file exists
    assert os.path.exists(owl_file)

    updateReadme = UpdateTermReadme(owl_file)

    readme_file = os.path.join(class_termsPATH, 'README.md')
    updateReadme.update_readme(readme_file)


