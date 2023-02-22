#!/usr/bin/env python3

# NOTICE
# This software was produced for the U.S. Government under contract FA8702-22-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import argparse
import logging
import json
import os
from typing import Dict, Set

import rdflib.plugins.sparql
from rdflib import OWL, RDF, URIRef

CACHE_FILE = "../version_mappings_cache.json"

NS_OWL = OWL
NS_RDF = RDF


def debug_printlinks(symlinks: Dict[str, str]) -> None:
    """Outputs the contents of the symlinks dict, for debugging only."""

    for src, dst in symlinks.items():
        logging.debug(repr(src) + " -> " + repr(dst))

def write_cache(mappings: Dict[str, str]) -> bool:
    """Writes a dictionary to a json file on as cache."""

    try:
        with open(CACHE_FILE, 'w+') as wp:
            json.dump(mappings, wp, indent=4)
            print(f'Wrote cache to {CACHE_FILE}')
        return True
    except Exception as e:
        print(f'Failed to write cache file: {e}')
        return False

def create_symlinks(top_srcdir: str, symlinks: Dict[str, str]) -> None:
    """Create symlinks based on generated gendoc -> web path."""

    _pre_cwd = os.getcwd()
    logging.debug("_pre_cwd = %r.", _pre_cwd)
    os.chdir(top_srcdir)
    logging.debug("os.getcwd() = %r.", os.getcwd())

    # TODO: research if more flags need to be specified for the symlink() func, what if we lack perms etc?
    for src, dst in symlinks.items():
        namespace_dir = os.path.dirname(dst)
        concept_file_basename = os.path.basename(dst)
        os.makedirs(namespace_dir, exist_ok=True)
        os.chdir(namespace_dir)
        logging.debug("os.getcwd() = %r.", os.getcwd())
        if not os.path.isfile(src):
            logging.error("os.getcwd() = %r.", os.getcwd())
            raise FileNotFoundError(src)
        try:
            os.symlink(src, concept_file_basename)
        except Exception as e:
            print(f'there was an error {e}')
        os.chdir(top_srcdir)

    # end method with resetting cwd
    os.chdir(_pre_cwd)
    logging.debug("os.getcwd() = %r.", os.getcwd())

def main() -> None:
    # parse arguments for ontology file we are preparing links for
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('--ontology-base', default="https://ontology.caseontology.org", help="Restrict mapped concepts to start with only this domain.")
    parser.add_argument('inTtl', type=str, help='ttl file to build sym-links off of')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    # allow query on ontology file
    graph = rdflib.Graph()
    graph.parse(args.inTtl)

    # Inherit prefixes defined in input context dictionary.
    nsdict = {k:v for (k,v) in graph.namespace_manager.namespaces()}

    # hold gendoc location, associated to symlinked path -- dict(gendocs-path : symlink)
    mappings: Dict[str, str] = dict()

    # Find all ontology-level IRIs and version IRIs.
    # (These IRIs are for the OWL ontologies and their versions, not for classes, shapes, etc.)
    # With HTML requests, these will all map to the documentation root.
    n_ontology_concepts: Set[URIRef] = set()
    for triple in graph.triples((None, NS_OWL.backwardCompatibleWith, None)):
        assert isinstance(triple[0], URIRef)
        assert isinstance(triple[2], URIRef)
        n_ontology_concepts.add(triple[0])
        n_ontology_concepts.add(triple[2])
    for triple in graph.triples((None, NS_OWL.imports, None)):
        assert isinstance(triple[0], URIRef)
        assert isinstance(triple[2], URIRef)
        n_ontology_concepts.add(triple[0])
        n_ontology_concepts.add(triple[2])
    for triple in graph.triples((None, NS_OWL.incompatibleWith, None)):
        assert isinstance(triple[0], URIRef)
        assert isinstance(triple[2], URIRef)
        n_ontology_concepts.add(triple[0])
        n_ontology_concepts.add(triple[2])
    for triple in graph.triples((None, NS_OWL.priorVersion, None)):
        assert isinstance(triple[0], URIRef)
        assert isinstance(triple[2], URIRef)
        n_ontology_concepts.add(triple[0])
        n_ontology_concepts.add(triple[2])
    for triple in graph.triples((None, NS_OWL.versionIRI, None)):
        assert isinstance(triple[0], URIRef)
        assert isinstance(triple[2], URIRef)
        n_ontology_concepts.add(triple[0])
        n_ontology_concepts.add(triple[2])
    for triple in graph.triples((None, NS_OWL.versionInfo, None)):
        assert isinstance(triple[0], URIRef)
        n_ontology_concepts.add(triple[0])
    for triple in graph.triples((None, NS_RDF.type, NS_OWL.Ontology)):
        assert isinstance(triple[0], URIRef)
        n_ontology_concepts.add(triple[0])
    for n_ontology_concept in sorted(n_ontology_concepts):
        ontology_concept_iri = n_ontology_concept
        if not ontology_concept_iri.startswith(args.ontology_base):
            continue
        ontology_url_path: str = ontology_concept_iri.split("ontology.org")[1]
        mappings[ontology_url_path] = "/documentation/index.html"

    # select class and property concepts from ontology -- dict(prefix : query)
    queries = dict()
    queries["class"] = """\
SELECT ?nConcept
WHERE {
  ?nConcept a owl:Class .
}"""
    queries["prop"] = """\
SELECT ?nConcept
WHERE {
  { ?nConcept a owl:DatatypeProperty . }
  UNION
  { ?nConcept a owl:ObjectProperty . }
}"""
    queries["shape"] = """\
SELECT ?nConcept
WHERE {
  { ?nConcept a sh:NodeShape . }
  UNION
  { ?nConcept a sh:PropertyShape . }
  UNION
  { ?nConcept a sh:Shape . }
}"""

    n_concepts_seen: Set[URIRef] = set()

    # generate paths for symlink src/dst locations
    tally = 0
    # Iterate over queries dictionary in this prefix order, in order to avoid conflicts between classes and node shapes.
    for prefix in [
        "class",
        "prop",
        "shape"
    ]:
        query = queries[prefix]
        select_query_object = rdflib.plugins.sparql.processor.prepareQuery(query, initNs=nsdict)
        for (row_no, row) in enumerate(graph.query(select_query_object)):
            if not isinstance(row[0], URIRef):
                continue
            n_concept = row[0]

            concept_iri = row[0].toPython()
            if not concept_iri.startswith(args.ontology_base):
                continue

            if n_concept in n_concepts_seen:
                continue
            n_concepts_seen.add(n_concept)
            
            tally = row_no + 1

            # determine URL path (file path, relative to service root within file system)
            # the split-point is the string in common to CASE's and UCO's IRIs.
            url_path: str = concept_iri.split("ontology.org")[1]

            # determine path to symlink target (gendocs HTML file), relative to basename of URL path
            iri_parts = concept_iri.split("/")
            gendocs_target = f"/documentation/{prefix}-{iri_parts[-2]}{iri_parts[-1].lower()}.html"

            # format mapping as absolute request path -> absolute path to documentation HTML;
            # "absolute" is relative to top_srcdir
            mappings[url_path] = gendocs_target

    if tally == 0:
        logging.warning(f"Found neither classes nor properties in input graph-file %r." % args.inTtl)

    write_cache(mappings)

if __name__ == "__main__":
    main()
