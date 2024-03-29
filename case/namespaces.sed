#!/usr/bin/sed

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

# This set of sed commands is intended to expand XML Entities found to
# be used but not defined in rdf-toolkit output.

s_&uco-action;_https://ontology.unifiedcyberontology.org/uco/action/_g
s_&case;_https://ontology.caseontology.org/case/case/_g
s_&uco-core;_https://ontology.unifiedcyberontology.org/uco/core/_g
s_&uco-identity;_https://ontology.unifiedcyberontology.org/uco/identity/_g
s_&investigation;_https://ontology.caseontology.org/case/investigation/_g
s_&uco-location;_https://ontology.unifiedcyberontology.org/uco/location/_g
s_&uco-marking;_https://ontology.unifiedcyberontology.org/uco/marking/_g
s_&uco-observable;_https://ontology.unifiedcyberontology.org/uco/observable/_g
s_&owl;_http://www.w3.org/2002/07/owl#_g
s_&uco-pattern;_https://ontology.unifiedcyberontology.org/uco/pattern/_g
s_&rdf;_http://www.w3.org/1999/02/22-rdf-syntax-ns#_g
s_&rdfs;_http://www.w3.org/2000/01/rdf-schema#_g
s_&uco-role;_https://ontology.unifiedcyberontology.org/uco/role/_g
s_&sh;_http://www.w3.org/ns/shacl#_g
s_&uco-time;_https://ontology.unifiedcyberontology.org/uco/time/_g
s_&uco-tool;_https://ontology.unifiedcyberontology.org/uco/tool/_g
s_&uco-types;_https://ontology.unifiedcyberontology.org/uco/types/_g
s_&uco-victim;_https://ontology.unifiedcyberontology.org/uco/victim/_g
s_&vocab;_https://ontology.caseontology.org/case/vocabulary/_g
s_&vocabulary;_https://ontology.caseontology.org/case/vocabulary/_g
s_&uco-vocabulary;_https://ontology.unifiedcyberontology.org/uco/vocabulary/_g
s_&xsd;_http://www.w3.org/2001/XMLSchema#_g
