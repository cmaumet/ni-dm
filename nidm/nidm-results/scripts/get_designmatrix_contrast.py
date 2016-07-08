import urllib2
import rdflib

# NIDM-Results document on NeuroVault
url = 'http://neurovault.org/collections/1435/spm_ds005_sub-01.nidm.ttl'
data = urllib2.urlopen(url)

g = rdflib.Graph()
g.parse(data, format="turtle")

# Retreive the design matrix as a csv file and the contrasts (name and vector)
query = """
prefix prov: <http://www.w3.org/ns/prov#>
prefix nidm_DesignMatrix: <http://purl.org/nidash/nidm#NIDM_0000019>
prefix obo_contrastweightmatrix: <http://purl.obolibrary.org/obo/STATO_0000323>
prefix nidm_contrastName: <http://purl.org/nidash/nidm#NIDM_0000085>

    SELECT DISTINCT ?location ?conname ?convec WHERE {
        ?design a nidm_DesignMatrix: ;
            prov:atLocation ?location ;
            dct:format "text/csv"^^xsd:string .
        ?con_est prov:used/prov:wasGeneratedBy/prov:used ?design ;
            prov:used ?contrast .
        ?contrast a obo_contrastweightmatrix: ;
            prov:value ?convec ;
            nidm_contrastName: ?conname .
        }
"""
contrasts = g.query(query)

if contrasts:
    for csv_file, conname, convec in contrasts:
        print "Contrast '" + conname + "': " + convec
        print "Design matrix available at " + csv_file
        print "---"
else:
    print "query failed!"
