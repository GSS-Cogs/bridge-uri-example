#%%

import rdflib

g = rdflib.Graph()
g.parse("./data.ttl", format="turtle")
g.parse("./codelist.ttl", format="turtle")

#%%

# Replace all local uris in the qb 
g.update("""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    DELETE { ?s ?p ?localConcept } 
    INSERT { ?s ?p ?foreignConcept } 
    WHERE {
        ?localConcept a skos:Concept ;
            owl:sameAs ?foreignConcept .

        ?s ?p ?localConcept .
    }
""")

#%%

# Replace all local uris in the concept scheme
g.update("""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    DELETE { ?localConcept ?p ?o } 
    INSERT { ?foreignConcept ?p2 ?o2 }
    WHERE {
        ?localConcept a skos:Concept ;
            owl:sameAs ?foreignConcept .

        ?localConcept ?p ?o .
        ?localConcept ?p2 ?o2 .

        FILTER (?p2 != owl:sameAs)
    }
""")

#%%

g.serialize(destination="./to-pmd.ttl", format="ttl")