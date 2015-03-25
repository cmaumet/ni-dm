#!/usr/bin/env python
'''Read an owl file and extract interesting information

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>
@copyright: University of Warwick 2014
'''

from rdflib import RDF, term
from rdflib.graph import Graph
from Constants import *
import urllib
import warnings

class OwlReader():

    def __init__(self, owl_file, import_owl_files=None):
        self.file = owl_file   
        self.import_files = import_owl_files
        self.graph = self.get_graph()
        
        # Retreive all classes defined in the owl file
        self.classes = self.get_class_names() 
        self.properties = self.get_property_names()
        # For each class find out attribute list as defined by domain in attributes
        self.attributes, self.ranges, self.type_restrictions, self.parent_ranges = self.get_attributes()


    def get_class_names(self):
        # Add PROV sub-types
        sub_types = set([PROV['Bundle'], PROV['Location'], PROV['Collection']]);

        for class_name in self.graph.subjects(RDF['type'], OWL['Class']):
            if not isinstance(class_name, term.BNode):
                sub_types.add(class_name)

        return sub_types

    def get_class_names_by_prov_type(self, classes=None, prefix=None, but=None):
        class_names = dict()
        # We at least want to have an output for Entity, Activity and Agent
        class_names[PROV['Entity']] = list()
        class_names[PROV['Activity']] = list()
        class_names[PROV['Agent']] = list()
        
        class_names[None] = list()

        if not classes:
            classes = self.graph.subjects(RDF['type'], OWL['Class'])
            # FIXME: Is there a more efficient way?
            if prefix:
                original_classes = classes
                classes = list()
                for class_name in original_classes:
                    if class_name.startswith(prefix):
                        classes.append(class_name)
            if but:
                classes = list(set(classes) - set(but))

        for class_name in classes:
            if not isinstance(class_name, term.BNode):
                prov_type = self.get_prov_class(class_name)
                if prov_type:
                    class_names.setdefault(prov_type, list()).append(class_name)
                else:
                    prov_type_found = False
                    parent_classes = list(self.graph.objects(class_name, RDFS['subClassOf']))
                    for parent_class in parent_classes:
                        prov_type = self.get_prov_class(parent_class, recursive=3)
                        if prov_type:
                            class_names.setdefault(prov_type, list()).append(class_name)
                            prov_type_found = True
                        # else:
                        #     parent_classes_2 = list(self.graph.objects(parent_class, RDFS['subClassOf']))
                        #     for parent_class_2 in parent_classes_2:
                        #         prov_type = self.get_prov_class(parent_class_2)
                        #         if prov_type:
                        #             class_names[prov_type].append(class_name)
                        #             prov_type_found = True
                        #         else:
                        #             parent_classes_3 = list(self.graph.objects(parent_class, RDFS['subClassOf']))
                        #             for parent_class_3 in parent_classes_3:
                        #                 prov_type = self.get_prov_class(parent_class_3)
                        #                 if prov_type:
                        #                     class_names[prov_type].append(class_name)
                        #                     prov_type_found = True

                    if not prov_type_found:
                        warnings.warn('No PROV type for class: '+self.graph.qname(class_name))
                        class_names.setdefault(None, list()).append(class_name)
                        
        return class_names

    def get_property_names(self):
        properties = set();
        for class_name in self.graph.subjects(RDF['type'], OWL['DatatypeProperty']):
            properties.add(class_name)
        for class_name in self.graph.subjects(RDF['type'], OWL['ObjectProperty']):
            properties.add(class_name)
        return properties

    def get_attributes(self):
        attributes = dict()
        # For each ObjectProperty found out corresponding range
        ranges = dict()

        parent_ranges = dict()

        restrictions = dict()

        # Check owl restrictions on classes
        for class_name in self.graph.subjects(RDF['type'], OWL['Class']):
            for class_restr in self.graph.objects(class_name, RDFS['subClassOf']):
                if isinstance(class_restr, term.BNode):
                    for prop in self.graph.objects(class_restr,OWL['onProperty']):
                        attributes.setdefault(class_name, set([prop])).add(prop)
                        for child_class in self.graph.subjects(RDFS['subClassOf'], class_name): 
                            attributes.setdefault(child_class, set([prop])).add(prop)

        # Attributes that can be found in all classes
        for data_property,p,o in self.graph.triples((None, RDF['type'], None)):
            if o == OWL['DatatypeProperty'] or o == OWL['ObjectProperty']:
                for class_name in self.graph.objects(data_property, RDFS['domain']):
                    # Add attribute to current class
                    if class_name in attributes:
                        attributes[class_name].add(data_property)
                    else:
                        attributes[class_name] = set([data_property])
                    
                    # Add attribute to children of current class
                    for child_class in self.graph.subjects(RDFS['subClassOf'], class_name):
                        # Add attribute to current class
                        if child_class in attributes:
                            attributes[child_class].add(data_property)
                        else:
                            attributes[child_class] = set([data_property])
                        class_name = child_class
                        
                for range_name in self.graph.objects(data_property, RDFS['range']):
                    # More complex type including restrictions
                    if isinstance(range_name, term.BNode):
                        for restriction_node in self.graph.objects(range_name, OWL['withRestrictions']):
                            for first_restriction in self.graph.objects(restriction_node, RDF['first']):
                                xsd_restrictions = set(['minInclusive', 'minExclusive', 'maxInclusive', 'maxExclusive'])
                                for xsd_restriction in xsd_restrictions:
                                    for min_incl in self.graph.objects(first_restriction, XSD[xsd_restriction]):
                                        if (data_property in restrictions):
                                            if (xsd_restriction in restrictions[data_property]):
                                                restrictions[data_property] = max(restrictions[data_property][xsd_restriction], min_incl)
                                            else:
                                                restrictions[data_property] = { xsd_restriction: min_incl}
                                        else:
                                            restrictions[data_property] = { xsd_restriction: min_incl}

                        for sub_range_name in self.graph.objects(range_name, OWL['onDatatype']):
                            range_name = sub_range_name


                    parent_ranges.setdefault(data_property, set()).add(range_name)

                    # Add child_class to range (for ObjectProperty)
                    for child in self.graph.transitive_subjects(RDFS['subClassOf'], range_name):
                        ranges.setdefault(data_property, set()).add(child)
                    

        return list((attributes, ranges, restrictions, parent_ranges))

    def get_graph(self):
        # Read owl (turtle) file
        owl_graph = Graph()
        if self.file[0:4] == "http":
            owl_txt = urllib.urlopen(self.file).read()
        else:
            owl_txt = open(self.file, 'r').read()

        # This is a workaround to avoid issue with "#" in base prefix as 
        # described in https://github.com/RDFLib/rdflib/issues/379,
        # When the fix is introduced in rdflib these 2 lines will be replaced by:
        # self.owl.parse(owl_file, format='turtle')
        owl_txt = owl_txt.replace("http://www.w3.org/2002/07/owl#", 
                        "http://www.w3.org/2002/07/owl")
        owl_graph.parse(data=owl_txt, format='turtle')

        if self.import_files:
            for import_file in self.import_files:
                # Read owl (turtle) file
                import_graph = Graph()
                if self.file[0:4] == "http":
                    import_txt = urllib.urlopen(import_file).read()
                else:
                    import_txt = open(import_file, 'r').read()

                # This is a workaround to avoid issue with "#" in base prefix as 
                # described in https://github.com/RDFLib/rdflib/issues/379,
                # When the fix is introduced in rdflib these 2 lines will be replaced by:
                # self.owl.parse(owl_file, format='turtle')
                import_txt = import_txt.replace("http://www.w3.org/2002/07/owl#", 
                                "http://www.w3.org/2002/07/owl")
                import_graph.parse(data=import_txt, format='turtle')

                owl_graph = owl_graph + import_graph

        return owl_graph


    def get_prov_class(self, owl_term, recursive=3):
        if not isinstance(owl_term, term.BNode) and \
            self.graph.qname(owl_term).startswith("prov:"):
            prov_class = owl_term
        else:
            parent_classes = list(self.graph.objects(owl_term, RDFS['subClassOf']))

            prov_class = None
            for parent_class in parent_classes:
                if not isinstance(parent_class, term.BNode):
                    if self.graph.qname(parent_class).startswith("prov:"):
                        prov_class = parent_class
                        break;

            if not prov_class:
                if recursive > 0:
                    parent_classes_super = parent_classes
                    for parent_class_super in parent_classes_super:
                        if not isinstance(parent_class_super, term.BNode):
                            prov_class = self.get_prov_class(parent_class_super, recursive=recursive-1)
                            if prov_class is not None:
                                break


        # Get mor generic PROV types
        if prov_class in set([PROV['SoftwareAgent'], PROV['Organization'], \
            PROV['Person']]):
            prov_class = PROV['Agent']
        if prov_class in set([PROV['Collection'], PROV['Location'], \
            PROV['Bundle'], PROV['Plan'], PROV['EmptyCollection']]):
            prov_class = PROV['Entity']
        if prov_class in set([PROV['Usage'], PROV['AgentInfluence'], \
                    PROV['Derivation'], PROV['PrimarySource'], \
                    PROV['ActivityInfluence'], PROV['Delegation'], 
                    PROV['Start'], PROV['EntityInfluence'], PROV['Quotation'],\
                    PROV['End'], PROV['Attribution'], PROV['Association'], \
                    PROV['Revision'], PROV['Communication'], \
                    PROV['Generation']]):
            prov_class = PROV['Influence']
        if prov_class == PROV['Invalidation']:
            prov_class = PROV['InstantaneousEvent']

        return prov_class

    def get_definition(self, owl_term):
        definition = list(self.graph.objects(owl_term, OBO_DEFINITION))
        if definition:
            definition = unicode(definition[0])
        else:
            definition = ""

        # Remove final dot if present
        if definition:
            if definition[-1] == ".":
                definition = definition[:-1]

        return definition

    def get_same_as(self, owl_term):
        same_as = list(self.graph.objects(owl_term, OWL['sameAs']))
        if same_as:
            same_as = ", ".join(same_as)
        else:
            same_as = ""
        return same_as

    def get_used_by(self, owl_term):
        used_by = list(self.graph.objects(owl_term, PROV['used']))
        return used_by

    def get_generated_by(self, owl_term):
        generated_by = list(self.graph.objects(owl_term, PROV['wasGeneratedBy']))
        return generated_by

    def get_example(self, owl_term, base_repository=None):
        example_list = list()

        examples = list(self.graph.objects(owl_term, OBO_EXAMPLE))

        for example in examples:
            if base_repository is not None:
                if example.startswith(base_repository):
                    local_path = example.replace(base_repository, "./")
                    fid_ex = open(local_path)
                    example = fid_ex.read()
                    fid_ex.close()
            example_list.append(example)
            
        return example_list 

    def get_range(self, owl_term):
        ranges = list(self.graph.objects(owl_term, RDFS['range']))

        range_display = ""

        for range_value in ranges:
            if not isinstance(range_value, term.BNode):
                if isinstance(range_value, term.URIRef):
                    range_display += str(self.graph.qname(range_value))+" "
                else:
                    range_display += str(range_value)
        return range_display

    def get_domain(self, owl_term):
        domains = list(self.graph.objects(owl_term, RDFS['domain']))

        domain_display = ""

        for domain_value in sorted(domains):
            if isinstance(domain_value, term.URIRef):
                domain_display += str(self.graph.qname(domain_value))+" "
            else:
                domain_display += str(domain_value)
        return domain_display

    def get_curation_status(self, owl_term):
        curation_status = list(self.graph.objects(owl_term, HAS_CURATION_STATUS))
        if curation_status:
            curation_status = curation_status[0]
        else:
            # By default consider that term is "uncurated"
            curation_status = OBO_UNCURATED    
        return curation_status

    def get_editor(self, owl_term):
        editor = list(self.graph.objects(owl_term, OBO_TERM_EDITOR))
        if editor:
            editor = " (editor: "+editor[0]+")"
        else:
            editor = ""
        return editor

    def get_editor_note(self, owl_term):
        editor_note = list(self.graph.objects(owl_term, OBO_EDITOR_NOTE))
        if editor_note:
            editor_note = " ("+editor_note[0]+")"
        else:
            editor_note = ""
        return editor_note

    def get_sub_class_names(self):
        sub_types = set()

        prov_types = set([PROV['Entity'], PROV['Activity'], PROV['Agent']])
        for prov_type in prov_types:
            for instance_id in self.graph.subjects(RDF.type, prov_type):
                for class_name in self.graph.objects(instance_id, RDF.type):
                   if not class_name == prov_type:
                        sub_types.add(class_name)

        return sub_types


    def check_class_names(self, example_graph, example_name):
        my_exception = dict()
        class_names = self.get_class_names()
        sub_types = self.get_sub_class_names()

        for not_recognised_sub_type in (sub_types - class_names):

            if not not_recognised_sub_type.startswith(str(PROV)):
                # key = example_graph.qname(not_recognised_sub_type)
                key = "\n Unrecognised sub-type: "+example_graph.qname(not_recognised_sub_type)
                if key in my_exception:
                    my_exception[key].add(example_name)
                else:
                    my_exception[key] = set([example_name])

        return my_exception

    def check_attributes(self, example_graph, example_name):
        ignored_attributes = set([   
                        RDFS['label'], 
                        RDF['type'],
                        PROV['value'], PROV['atTime'], PROV['used'], PROV['wasAssociatedWith'],
                        PROV['qualifiedGeneration'], PROV['wasGeneratedBy'], PROV['atLocation'], 
                        PROV['wasDerivedFrom'], 
                        CRYPTO['sha512']
                        ])  

        my_exception = dict()
        my_range_exception = dict()
        my_restriction_exception = dict()

        owl_attributes = self.attributes
        owl_ranges = self.ranges
        owl_restrictions = self.type_restrictions

        # if not owl_attributes or not owl_ranges:
        #     if owl_file is None:
        #         raise Exception("One of class_names or owl_file must be not None.")
        #     else:
        #         owl_graph = get_owl_graph(owl_file, owl_imports)

        #         attributes_ranges = get_attributes_from_owl(owl_graph)
        #         owl_attributes = attributes_ranges[0]
        #         owl_ranges = attributes_ranges[1]   
        #         owl_restrictions = attributes_ranges[2]

        # Find all attributes
        for s,p,o in example_graph.triples((None, None, None)):
            # To be a DataTypeProperty then o must be a literal
            # if isinstance(o, rdflib.term.Literal):
            if p not in ignored_attributes:
                # *** Check domain
                # Get all defined types of current object
                found_attributes = False
                class_names = ""
                for class_name in sorted(example_graph.objects(s, RDF['type'])):
                    attributes = owl_attributes.get(class_name)

                    # If the current class was defined in the owl file check if current
                    # attribute was also defined.
                    if attributes:
                        if p in attributes:
                            found_attributes = True

                    class_names += ", "+example_graph.qname(class_name)

                # if not found_attributes:
                    # if attributes:
                        # if not (p in attributes):
                if not found_attributes:
                    key = "\n Unrecognised attribute: "+example_graph.qname(p)+\
                                " in "+class_names[2:]
                    if not key in my_exception:
                        my_exception[key] = set([example_name])
                    else:
                        my_exception[key].add(example_name)


                # *** Check range for ObjectProperties and DataProperties
                if isinstance(o, term.URIRef):
                    # An ObjectProperty can point to an instance, then we look for its type:
                    found_range = set(example_graph.objects(o, RDF['type']))

                    # An ObjectProperty can point to a term
                    if not found_range:
                        found_range = set([o])

                        # If the term is an individual, look for its type
                        if OWL['NamedIndividual'] in \
                            set(self.graph.objects(o, RDF['type'])):
                            found_range = set(self.graph.objects(o, RDF['type']))

                elif isinstance(o, term.Literal):
                    found_range = set([o.datatype])

                correct_range = False
                if p in owl_ranges:
                    # If none of the class found for current ObjectProperty value is part of the range
                    # throw an error

                    # If the type of current value is within the authorised ranges
                    if found_range.intersection(owl_ranges[p]):
                        correct_range = True
                    else:
                        if p in owl_ranges:
                            # A bit more complicated to deal with "positiveInteger"
                            for owl_range in owl_ranges[p]:
                                # FIXME: we should be able to do better than that to check that XSD['positiveInteger'] is 
                                # in owl_ranges[p]
                                if (XSD['positiveInteger'] == owl_range) and\
                                     (next(iter(found_range)) == XSD['int']) and\
                                      (o.value >= 0):
                                        correct_range = True
                    if not correct_range:
                        found_range_line = ""
                        # FIXME: This should be better handled to be able to do "if found_range"
                        if not None in found_range:
                            found_range_line = ', '.join(map(example_graph.qname, sorted(found_range)))
                        owl_range_line = ""
                        if p in owl_ranges:
                            owl_range_line = ', '.join(map(example_graph.qname, sorted(owl_ranges[p])))

                        key = "\n Unrecognised range: "+\
                            found_range_line+\
                            ' for '+example_graph.qname(p)+' should be '+\
                            owl_range_line
                else:
                    # No range found for current attribute
                    correct_range = False
                    key = "\n No range defined for: "+\
                            example_graph.qname(p)

                if not correct_range:
                    if not key in my_range_exception:
                        my_range_exception[key] = set([example_name])
                    else:
                        my_range_exception[key].add(example_name)

                if p in owl_restrictions:
                    restrictions_ok = True
                    if 'minInclusive' in owl_restrictions[p]:
                        if o.value < owl_restrictions[p]['minInclusive'].value:
                            restrictions_ok = False
                    if 'minExclusive' in owl_restrictions[p]:
                        if o.value <= owl_restrictions[p]['minExclusive'].value:
                            restrictions_ok = False
                    if 'maxInclusive' in owl_restrictions[p]:
                        if o.value > owl_restrictions[p]['maxInclusive'].value:
                            restrictions_ok = False
                    if 'maxExclusive' in owl_restrictions[p]:
                        if o.value >= owl_restrictions[p]['maxExclusive'].value:
                            restrictions_ok = False
                    if not restrictions_ok:
                        key = "\n Contraints: value "+str(o.value)+\
                            ' for '+example_graph.qname(p)+' does not observe contraints '+\
                            ', '.join(sorted(owl_restrictions[p]))
                        if not key in my_restriction_exception:
                            my_restriction_exception[key] = set([example_name])
                        else:
                            my_restriction_exception[key].add(example_name)

        return list((my_exception, my_range_exception, my_restriction_exception))
