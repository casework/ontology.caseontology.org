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

top_srcdir := $(shell cd .. ; pwd)

CURRENT_RELEASE ?=
ifeq ($(CURRENT_RELEASE),)
$(error CURRENT_RELEASE not defined - did you call 'make' from one directory up?)
endif

RDF_TOOLKT_JAR := $(top_srcdir)/dependencies/CASE/dependencies/UCO/lib/rdf-toolkit.jar

version_iri_files := \
  case/$(CURRENT_RELEASE).rdf \
  case/$(CURRENT_RELEASE).ttl \
  investigation/$(CURRENT_RELEASE).rdf \
  investigation/$(CURRENT_RELEASE).ttl \
  vocabulary/$(CURRENT_RELEASE).rdf \
  vocabulary/$(CURRENT_RELEASE).ttl

all: \
  $(version_iri_files)

case.rdf: \
  $(top_srcdir)/dependencies/CASE/ontology/master/case.ttl \
  $(RDF_TOOLKT_JAR) \
  namespaces.sed
	rm -f __$@ _$@
	java -jar $(RDF_TOOLKT_JAR) \
	  --inline-blank-nodes \
	  --source $< \
	  --source-format turtle \
	  --target __$@ \
	  --target-format rdf-xml
	sed \
	  -f namespaces.sed \
	  __$@ \
	  > _$@
	xmllint \
	  --noout \
	  _$@
	rm __$@
	mv _$@ $@

case.ttl: \
  $(top_srcdir)/dependencies/CASE/ontology/master/case.ttl
	cp $< $@

case/$(CURRENT_RELEASE).rdf: \
  case.rdf
	mkdir -p case
	cp $< $@

case/$(CURRENT_RELEASE).ttl: \
  case.ttl
	mkdir -p case
	cp $< $@

clean:
	@rm -f \
	  *.rdf \
	  *.ttl \
	  .*.done.log

investigation.rdf: \
  $(top_srcdir)/dependencies/CASE/ontology/investigation/investigation.ttl \
  $(RDF_TOOLKT_JAR) \
  namespaces.sed
	java -jar $(RDF_TOOLKT_JAR) \
	  --inline-blank-nodes \
	  --source $< \
	  --source-format turtle \
	  --target __$@ \
	  --target-format rdf-xml
	sed \
	  -f namespaces.sed \
	  __$@ \
	  > _$@
	rm __$@
	mv _$@ $@

investigation.ttl: \
  $(top_srcdir)/dependencies/CASE/ontology/investigation/investigation.ttl
	cp $< $@

investigation/$(CURRENT_RELEASE).rdf: \
  investigation.rdf
	mkdir -p investigation
	cp $< $@

investigation/$(CURRENT_RELEASE).ttl: \
  investigation.ttl
	mkdir -p investigation
	cp $< $@

vocabulary.rdf: \
  $(top_srcdir)/dependencies/CASE/ontology/vocabulary/vocabulary.ttl \
  $(RDF_TOOLKT_JAR) \
  namespaces.sed
	java -jar $(RDF_TOOLKT_JAR) \
	  --inline-blank-nodes \
	  --source $< \
	  --source-format turtle \
	  --target __$@ \
	  --target-format rdf-xml
	sed \
	  -f namespaces.sed \
	  __$@ \
	  > _$@
	rm __$@
	mv _$@ $@

vocabulary.ttl: \
  $(top_srcdir)/dependencies/CASE/ontology/vocabulary/vocabulary.ttl
	cp $< $@

vocabulary/$(CURRENT_RELEASE).rdf: \
  vocabulary.rdf
	mkdir -p vocabulary
	cp $< $@

vocabulary/$(CURRENT_RELEASE).ttl: \
  vocabulary.ttl
	mkdir -p vocabulary
	cp $< $@
