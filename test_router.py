#!/usr/bin/env python3

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

import logging
import os
from typing import List, Optional, Set, Tuple

import flask
import flask.testing
import pytest

import router.app


@pytest.fixture
def host_prefix() -> str:
    _host_prefix = os.getenv("HOST_PREFIX")
    if _host_prefix is None:
        raise ValueError(
            "Unable to retrieve host prefix from process environment.  Please set the environment variable HOST_PREFIX before calling pytest."
        )
    if _host_prefix.startswith("http://"):
        logging.info("Host prefix updated to use https scheme.")
        _host_prefix = _host_prefix.replace("http://", "https://")
    return _host_prefix


@pytest.fixture
def app() -> flask.Flask:
    return router.app.app


@pytest.mark.parametrize(
    [
        "url_path",
        "accept_content_type",
        "expected_matching_file",
        "expected_response_content_type",
    ],
    [
        ("/case/vocabulary.rdf", None, "case/vocabulary.rdf", "application/rdf+xml"),
        (
            "/case/vocabulary.rdf",
            "application/rdf+xml",
            "case/vocabulary.rdf",
            "application/rdf+xml",
        ),
        ("/case/vocabulary.ttl", None, "case/vocabulary.ttl", "text/turtle"),
        ("/case/vocabulary.ttl", "text/turtle", "case/vocabulary.ttl", "text/turtle"),
    ],
)
def test_status_200(
    app: flask.Flask,
    client: flask.testing.FlaskClient,
    url_path: str,
    accept_content_type: Optional[str],
    expected_matching_file: str,
    expected_response_content_type: str,
) -> None:
    headers: List[Tuple[str, str]] = []
    if accept_content_type is not None:
        headers.append(("Accept", accept_content_type))
    response = client.get(url_path, headers=headers)
    assert 200 == response.status_code
    assert expected_response_content_type == response.mimetype
    with open(expected_matching_file, "rb") as match_fh:
        assert match_fh.read() == response.data


@pytest.mark.parametrize(
    ["url_path", "accept_content_type", "user_agent", "expected_location"],
    [
        (
            "/",
            None,
            None,
            "/documentation/index.html",
        ),
        (
            # Confirm non-umbrella ontology request is redirected to umbrella documentation index when HTML content is requested, regardless of user agent.
            "/case/case",
            "text/html",
            "Java/1.8.0_332",
            "/documentation/index.html",
        ),
        (
            # Confirm umbrella ontology request is redirected to RDF-XML ontology file with org.semanticweb.owlapi behavior.
            "/case/case",
            None,
            "Java/1.8.0_332",
            "/case/case.rdf",
        ),
        (
            # Confirm non-umbrella ontology request is assumed to be RDF-XML request.
            "/case/investigation",
            None,
            None,
            "/case/investigation.rdf",
        ),
        (
            # Confirm non-umbrella ontology request is redirected to RDF-XML ontology file with org.semanticweb.owlapi behavior.
            "/case/investigation",
            None,
            "Java/1.8.0_332",
            "/case/investigation.rdf",
        ),
        (
            # Confirm non-umbrella ontology version request is redirected to RDF-XML ontology file with org.semanticweb.owlapi behavior.
            "/case/investigation/1.2.0",
            None,
            "Java/1.8.0_332",
            "/case/investigation/1.2.0.rdf",
        ),
        (
            "/case/investigation",
            "application/rdf+xml",
            None,
            "/case/investigation.rdf",
        ),
        (
            "/case/investigation",
            "text/html",
            None,
            "/documentation/index.html",
        ),
        (
            "/case/investigation",
            "text/turtle",
            None,
            "/case/investigation.ttl",
        ),
        (
            # Confirm prefix IRI (/namespace IRI) redirects to umbrella documentation index.
            "/case/investigation/",
            None,
            None,
            "/documentation/index.html",
        ),
        (
            # Confirm version IRI request is assumed to be RDF-XML request.
            "/case/investigation/1.0.0",
            None,
            None,
            "/case/investigation/1.0.0.rdf",
        ),
        (
            "/case/investigation/1.0.0",
            "application/rdf+xml",
            None,
            "/case/investigation/1.0.0.rdf",
        ),
        (
            # Confirm version IRI request as HTML is redirected to umbrella documentation index.
            "/case/investigation/1.0.0",
            "text/html",
            None,
            "/documentation/index.html",
        ),
        (
            "/case/investigation/1.0.0",
            "text/turtle",
            None,
            "/case/investigation/1.0.0.ttl",
        ),
        (
            "/case/investigation/ProvenanceRecord",
            None,
            None,
            "/documentation/class-investigationprovenancerecord.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/ProvenanceRecord",
        #     "application/rdf+xml",
        #     None,
        #     "/case/investigation/ProvenanceRecord.rdf",
        # ),
        (
            "/case/investigation/ProvenanceRecord",
            "text/html",
            None,
            "/documentation/class-investigationprovenancerecord.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/ProvenanceRecord",
        #     "text/turtle",
        #     None,
        #     "/case/investigation/ProvenanceRecord.ttl",
        # ),
        (
            "/case/investigation/exhibitNumber",
            None,
            None,
            "/documentation/prop-investigationexhibitnumber.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/exhibitNumber",
        #     "application/rdf+xml",
        #     None,
        #     "/case/investigation/exhibitNumber.rdf",
        # ),
        (
            "/case/investigation/exhibitNumber",
            "text/html",
            None,
            "/documentation/prop-investigationexhibitnumber.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/exhibitNumber",
        #     "text/turtle",
        #     None,
        #     "/case/investigation/exhibitNumber.ttl",
        # ),
    ],
)
def test_status_301(
    app: flask.Flask,
    client: flask.testing.FlaskClient,
    host_prefix: str,
    url_path: str,
    accept_content_type: Optional[str],
    user_agent: Optional[str],
    expected_location: str,
) -> None:
    """
    This test is intended to cover:
    * Concept structural types: Ontology, classes, properties, and shapes.  (CASE does not have a shape that is not also a class, so this last structural type is not currently covered.)
    * Interaction of the "Accept" header with the requested URL: When none is specified, or Turtle or RDF is requested.
    """
    headers: List[Tuple[str, str]] = []
    if accept_content_type is not None:
        headers.append(("Accept", accept_content_type))
    if user_agent is not None:
        headers.append(("User-Agent", user_agent))
    response = client.get(url_path, headers=headers)
    assert 301 == response.status_code
    assert host_prefix + expected_location == response.location


@pytest.mark.parametrize(
    ["url_path", "expected_status_codes"],
    [
        (".git", {403, 404}),
    ],
)
def test_status_40x(
    app: flask.Flask,
    client: flask.testing.FlaskClient,
    url_path: str,
    expected_status_codes: Set[int],
) -> None:
    """
    Test starting source:
    https://pytest-flask.readthedocs.io/en/latest/features.html#feature-reference
    """
    logging.debug(client)
    assert client.get(url_path).status_code in expected_status_codes
