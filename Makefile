#!/usr/bin/make -f

# Portions of this file contributed by NIST are governed by the following
# statement:
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

SHELL := /bin/bash

top_srcdir := $(shell pwd)

# Use HOST_PREFIX to test the deployment at the specified host.
# Syntax note - there is no trailing slash.
HOST_PREFIX ?= http://localhost

all: \
  iri_mappings_to_html.json \
  iri_mappings_to_rdf.json \
  iri_mappings_to_ttl.json

.PHONY: \
  check-service

.case.done.log: \
  current_ontology_version.txt \
  dependencies/CASE/tests/case_monolithic.ttl
	$(MAKE) \
	  CURRENT_RELEASE=$$(head -n1 current_ontology_version.txt) \
	  --directory case
	touch $@

.documentation.done.log: \
  current_ontology_version.txt \
  dependencies/CASE/tests/case_monolithic.ttl
	rm -rf documentation
	mkdir documentation
	source venv/bin/activate \
	  && ontospy gendocs \
	    --outputpath $$PWD/documentation \
	    --theme united \
	    --title case-$$(head -n1 current_ontology_version.txt)-docs \
	    --type 2 \
	    $(top_srcdir)/dependencies/CASE/tests/case_monolithic.ttl
	test -r documentation/index.html
	touch $@

# This target checks for a file's existence to confirm that the submodule
# has been checked out at least once.  To simplify development work, a
# submodule init-update is only run to do an initial checkout, so
# submodule-update doesn't reset a development pointer.
.git_submodule_init.done.log: \
  .gitmodules
	test -r dependencies/CASE/README.md \
	  || (git submodule init dependencies/CASE && git submodule update dependencies/CASE)
	# Initialize CASE submodules and retrieve rdf-toolkit.
	$(MAKE) \
	  --directory dependencies/CASE \
	  .git_submodule_init.done.log \
	  .lib.done.log
	touch $@

.venv.done.log: \
  .git_submodule_init.done.log \
  requirements.txt
	rm -rf venv
	python3 -m venv \
	  venv
	source venv/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools \
	    wheel
	source venv/bin/activate \
	  && pip install \
	    --requirement requirements.txt
	touch $@

# Test matrix:
# Concept broad type: ontology, class, or property
# "Accept" header: none specified, Turtle requested, or RDF requested
check-service:
	## XFAILs
	wget \
	  --output-document _$@ \
	  $(HOST_PREFIX)/.git \
	  ; rc=$$? ; test 8 -eq $$rc
	rm _$@
	## Ontologies
	wget \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/vocabulary.ttl
	diff _$@ case/vocabulary.ttl
	rm _$@
	wget \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/vocabulary.rdf
	diff _$@ case/vocabulary.rdf
	rm _$@
	wget \
	  --header 'Accept: text/turtle' \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/vocabulary
	diff _$@ case/vocabulary.ttl
	rm _$@
	wget \
	  --header 'Accept: application/rdf+xml' \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/vocabulary
	diff _$@ case/vocabulary.rdf
	rm _$@
	## Classes
	wget \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/investigation/ProvenanceRecord
	# NOTE - no comparison test done, default behavior just needs to not return a server error.
	rm _$@
	wget \
	  --header 'Accept: text/html' \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/investigation/ProvenanceRecord
	diff _$@ documentation/class-investigationprovenancerecord.html
	rm _$@
#	#TODO - Turtle breakout needs to be written.
#	wget \
#	  --header 'Accept: text/turtle' \
#	  --output-document _$@ \
#	  $(HOST_PREFIX)/case/investigation/ProvenanceRecord
#	diff _$@ case/investigation/ProvenanceRecord.ttl
#	rm _$@
#	#TODO - Turtle RDF-XML breakout needs to be written.
#	wget \
#	  --header 'Accept: application/rdf+xml' \
#	  --output-document _$@ \
#	  $(HOST_PREFIX)/case/investigation/ProvenanceRecord
#	diff _$@ case/investigation/ProvenanceRecord.rdf
#	rm _$@
	## Properties
	wget \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/investigation/exhibitNumber
	# NOTE - no comparison test done, default behavior just needs to not return a server error.
	rm _$@
	wget \
	  --header 'Accept: text/html' \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/investigation/exhibitNumber
	diff _$@ documentation/prop-investigationexhibitnumber.html
	rm _$@
#	#TODO - Turtle breakout needs to be written.
#	wget \
#	  --header 'Accept: text/turtle' \
#	  --output-document _$@ \
#	  $(HOST_PREFIX)/case/investigation/exhibitNumber
#	diff _$@ case/investigation/exhibitNumber.ttl
#	rm _$@
#	#TODO - Turtle RDF-XML breakout needs to be written.
#	wget \
#	  --header 'Accept: application/rdf+xml' \
#	  --output-document _$@ \
#	  $(HOST_PREFIX)/case/investigation/exhibitNumber
#	diff _$@ case/investigation/exhibitNumber.rdf
#	rm _$@
	# Confirm documentation index is reachable.
	wget \
	  --output-document _$@ \
	  $(HOST_PREFIX)/documentation/
	diff _$@ documentation/index.html
	rm _$@
	# Confirm HTML index for non-umbrella namespaces are redirected to umbrella documentation index.
	wget \
	  --header 'Accept: text/html' \
	  --output-document _$@ \
	  $(HOST_PREFIX)/case/investigation/
	diff _$@ documentation/index.html
	rm _$@
	@echo >&2
	@echo "INFO:Makefile:Service tests pass!" >&2

clean:
	@$(MAKE) \
	  CURRENT_RELEASE=$$(head -n1 current_ontology_version.txt) \
	  --directory case \
	  clean
	@rm -f .*.done.log
	@test ! -r dependencies/CASE/README.md \
	  || $(MAKE) \
	    --directory dependencies/CASE \
	    clean
	@# Revert status of test files, to avoid CASE submodule irrelevantly reporting as dirty.
	@cd dependencies/CASE \
	  && git checkout -- tests/examples

current_ontology_iris.txt: \
  .venv.done.log \
  dependencies/CASE/tests/case_monolithic.ttl \
  src/current_ontology_iris_txt.py
	source venv/bin/activate \
	  && python3 src/current_ontology_iris_txt.py \
	    --ontology-base https://ontology.caseontology.org \
	    _$@ \
	    dependencies/CASE/tests/case_monolithic.ttl
	mv _$@ $@

current_ontology_version.txt: \
  .git_submodule_init.done.log \
  .venv.done.log \
  src/current_ontology_version.py
	source venv/bin/activate \
	  && python3 src/current_ontology_version.py \
	    dependencies/CASE/ontology/master/case.ttl \
	    https://ontology.caseontology.org/case/case \
	    > _$@
	test -s _$@
	mv _$@ $@

dependencies/CASE/tests/case_monolithic.ttl: \
  .git_submodule_init.done.log
	$(MAKE) \
	  --directory dependencies/CASE/tests \
	  case_monolithic.ttl
	# Clean up superfluous artifact.  TODO - This step can be removed after the 0.3.0 release of the referenced tool.
	rm -rf dependencies/CASE/dependencies/UCO/dependencies/CASE-Utility-SHACL-Inheritance-Review/build
	# Guarantee file is built and timestamp is up to date.
	test -r $@
	touch $@

# Accumulate all ontology and version IRIs.
ontology_iris_archive.txt: \
  current_ontology_iris.txt
	cat $< > __$@
	test ! -r $@ \
	  || cat $@ >> __$@
	LC_ALL=C sort __$@ \
	  | uniq > _$@
	rm __$@
	mv _$@ $@

iri_mappings_to_html.json: \
  .documentation.done.log \
  ontology_iris_archive.txt \
  src/map_entries_to_gendocs.py
	source venv/bin/activate \
	  && cd src \
	    && python3 map_entries_to_gendocs.py \
	      --ontology-base https://ontology.caseontology.org \
	      $(top_srcdir)/dependencies/CASE/tests/case_monolithic.ttl \
	      $(top_srcdir)/ontology_iris_archive.txt

iri_mappings_to_rdf.json: \
  .case.done.log \
  ontology_iris_archive.txt \
  src/map_iris_to_graph_file.py
	source venv/bin/activate \
	  && python3 src/map_iris_to_graph_file.py \
	    --ontology-base https://ontology.caseontology.org \
	    _$@ \
	    application/rdf+xml \
	    ontology_iris_archive.txt
	mv _$@ $@

iri_mappings_to_ttl.json: \
  .case.done.log \
  ontology_iris_archive.txt \
  src/map_iris_to_graph_file.py
	source venv/bin/activate \
	  && python3 src/map_iris_to_graph_file.py \
	    --ontology-base https://ontology.caseontology.org \
	    _$@ \
	    text/turtle \
	    ontology_iris_archive.txt
	mv _$@ $@
