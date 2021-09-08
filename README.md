# bridge-uri-example

Example of how the "coining a bridge uri" proposal could work as part of https://github.com/GSS-Cogs/gss-utils/issues/210.

To generate the `ttl` output from the CSVW metadata in this repo:

```bash
docker run \
-v $PWD:/workspace \
-w /workspace \
--rm -it gsscogs/csv2rdf \
csv2rdf -u data.csv-metadata.json -m annotated -o data.ttl;

docker run \
-v $PWD:/workspace \
-w /workspace \
--rm -it gsscogs/csv2rdf \
csv2rdf -u codelist.csv-metadata.json -m annotated -o codelist.ttl; 
```

The `qb` output from `data.csv` includes "local" uris for countries, e.g. `<http://data.gov.uk/my-statistics/country/A>`.
```ttl
<http://data.gov.uk/my-statistics/obs/A> <http://data.gov.uk/measure/count> 1.0E2;
  <http://purl.org/linked-data/sdmx/2009/dimension#refArea> <http://data.gov.uk/my-statistics/country/A> .
```

The `skos` output from `codelist.csv` has `owl:sameAs` relations connecting the local country uris to the "official" country uris. `<http://data.gov.uk/my-statistics/country/A> -> <http://example.org/A>`.
```ttl
<http://data.gov.uk/my-statistics/country/A> a <http://www.w3.org/2004/02/skos/core#Concept>;
  <http://www.w3.org/2000/01/rdf-schema#label> "A";
  <http://www.w3.org/2002/07/owl#sameAs> <http://example.org/A>;
  <http://www.w3.org/2004/02/skos/core#inScheme> <http://data.gov.uk/my-statistics/codelist/country> .
```

So my goal is to change the data prior to load into PMD to make use of the proper uris. I use two SPARQL INSERT/DELETE queries to swap all uses of the local uris to the official ones (see [sparql-update.py](./sparql-update.py)).

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
DELETE { ?s ?p ?localConcept } 
INSERT { ?s ?p ?foreignConcept } 
WHERE {
    ?localConcept a skos:Concept ;
        owl:sameAs ?foreignConcept .

    ?s ?p ?localConcept .
}
```

```sparql
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
```
...and in the output the local uris are gone, and replaced by the official ones.

```ttl
# qb stuff:
<http://data.gov.uk/my-statistics/obs/A> <http://data.gov.uk/measure/count> 1e+02 ;
    <http://purl.org/linked-data/sdmx/2009/dimension#refArea> <http://example.org/A> .

# skos stuff:
<http://example.org/A> a <http://www.w3.org/2004/02/skos/core#Concept>;
  <http://www.w3.org/2000/01/rdf-schema#label> "A";
  <http://www.w3.org/2004/02/skos/core#inScheme> <http://data.gov.uk/my-statistics/codelist/country> .
```