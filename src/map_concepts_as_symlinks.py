#!/usr/bin/env python3

# NOTICE
# This software was produced for the U.S. Government under contract FA8702-22-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import argparse
import rdflib
import os
import rdflib.plugins.sparql

def debug_printlinks(symlinks):
    """Outputs the contents of the symlinks dict, for debugging only."""

    for src, dst in symlinks.items():
        print(repr(src) + " -> " + repr(dst))

def create_symlinks(symlinks):
    """Create symlinks based on generated gendoc -> web path."""

    # TODO: research if more flags need to be specified for the symlink() func, what if we lack perms etc?
    for src, dst in symlinks.items():
        os.symlink(src, dst)

def main():
    # parse arguments for ontology file & version we are preparing links for
    parser = argparse.ArgumentParser()
    parser.add_argument('inTtl', type=str, help='ttl file to build sym-links off of')
    parser.add_argument('--version', type=str, help='verson of the ontology (optional, example: 0.4.0)', required=False)
    args = parser.parse_args()

    # allow query on ontology file
    graph = rdflib.Graph()
    graph.parse(args.inTtl)

    # Inherit prefixes defined in input context dictionary.
    nsdict = {k:v for (k,v) in graph.namespace_manager.namespaces()}

    # select class and property concepts from ontology -- dict(prefix : query)
    queries = dict()
    queries["class"] = "SELECT ?nConcept WHERE { ?nConcept a owl:Class . }"
    queries["prop"] = "SELECT ?nConcept WHERE {{ ?nConcept a owl:DatatypeProperty . } UNION { ?nConcept a owl:ObjectProperty . }}"

    # hold gendoc location, assoicated to symlinked path -- dict(gendocs-path : symlink)
    symlinks = dict()

    # generate paths for symlink src/dst locations
    for prefix, query in queries.items():
        tally = 0
        select_query_object = rdflib.plugins.sparql.prepareQuery(query, initNs=nsdict)
        for (row_no, row) in enumerate(graph.query(select_query_object)):
            tally = row_no + 1
            uri_parts = row[0].toPython().split('/')

            # format gendoc -> symlink (src, dst) combos.. check if a version is specified
            src = f"../docs{f'/{args.version}' if args.version else ''}/{prefix}-{uri_parts[-2]}{uri_parts[-1]}.html"
            dst = f"case{f'/{args.version}' if args.version else ''}/{uri_parts[-2]}/{uri_parts[-1]}.html"
            symlinks[src] = dst

        if tally == 0:
            raise ValueError("Failed to return any results.") 

    debug_printlinks(symlinks)
    # create_symlinks(symlinks)

if __name__ == "__main__":
    main()