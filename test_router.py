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
    ["url_path", "accept_content_type", "expected_location"],
    [
        (
            "/",
            None,
            "/documentation/index.html",
        ),
        (
            # Confirm HTML index for non-umbrella namespaces are redirected to umbrella documentation index.
            "/case/investigation",
            None,
            "/documentation/index.html",
        ),
        (
            "/case/investigation",
            "application/rdf+xml",
            "/case/investigation.rdf",
        ),
        (
            "/case/investigation",
            "text/turtle",
            "/case/investigation.ttl",
        ),
        (
            # Confirm HTML index for non-umbrella namespaces are redirected to umbrella documentation index.
            "/case/investigation/",
            None,
            "/documentation/index.html",
        ),
        (
            # Confirm HTML index for non-umbrella namespaces are redirected to umbrella documentation index.
            "/case/investigation/1.0.0",
            None,
            "/documentation/index.html",
        ),
        (
            "/case/investigation/1.0.0",
            "application/rdf+xml",
            "/case/investigation/1.0.0.rdf",
        ),
        (
            # Confirm HTML index for non-umbrella namespaces are redirected to umbrella documentation index.
            "/case/investigation/1.0.0",
            "text/html",
            "/documentation/index.html",
        ),
        (
            "/case/investigation/1.0.0",
            "text/turtle",
            "/case/investigation/1.0.0.ttl",
        ),
        (
            "/case/investigation/ProvenanceRecord",
            None,
            "/documentation/class-investigationprovenancerecord.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/ProvenanceRecord",
        #     "application/rdf+xml",
        #     "/case/investigation/ProvenanceRecord.rdf",
        # ),
        (
            "/case/investigation/ProvenanceRecord",
            "text/html",
            "/documentation/class-investigationprovenancerecord.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/ProvenanceRecord",
        #     "text/turtle",
        #     "/case/investigation/ProvenanceRecord.ttl",
        # ),
        (
            "/case/investigation/exhibitNumber",
            None,
            "/documentation/prop-investigationexhibitnumber.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/exhibitNumber",
        #     "application/rdf+xml",
        #     "/case/investigation/exhibitNumber.rdf",
        # ),
        (
            "/case/investigation/exhibitNumber",
            "text/html",
            "/documentation/prop-investigationexhibitnumber.html",
        ),
        # TODO: Individual concept breakout needs to be written.
        # (
        #     "/case/investigation/exhibitNumber",
        #     "text/turtle",
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
