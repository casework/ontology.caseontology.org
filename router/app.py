import pathlib

from flask import Flask, request, redirect, abort
from datetime import datetime
import string
import json

app = Flask(__name__)

srcdir = pathlib.Path(__file__).parent
top_srcdir = srcdir / ".."

# load html mappings
with (top_srcdir / 'iri_mappings_to_html.json').open('r') as fp:
    html = json.load(fp)

# load rdf mappings
with (top_srcdir / 'iri_mappings_to_rdf.json').open('r') as fp:
    rdf = json.load(fp)

# load ttl mappings
with (top_srcdir / 'iri_mappings_to_ttl.json').open('r') as fp:
    ttl = json.load(fp)

@app.route("/")
def root():
    '''Routes the root '/' of the host to the index of the docs'''

    # redirect when we find a match based on SSL
    if request.is_secure:
        return redirect(f'https://{request.host}/case/documentation/index.html', 301)
    else:
        return redirect(f'http://{request.host}/case/documentation/index.html', 301)

@app.route("/<ontology>/<path:target>", methods=['GET'])
def router(ontology: str, target: str):
    '''Routes data through the file system to the appropriate documentation'''

    # TODO: based on content_type, route to specific html/ttl/rdf
    content_type = requests.headers.get('Content-Type')

    # check for HTML matches first
    if f"{ontology}/{target}" in html:
        location = html[f"{ontology}/{target}"]
        if request.is_secure:
            return redirect(f'https://{request.host}/{location}', 301)
        else:
            return redirect(f'http://{request.host}/{location}', 301)

    # check for RDF matches second
    if f"{ontology}/{target}" in rdf:
        location = rdf[f"{ontology}/{target}"]
        if request.is_secure:
            return redirect(f'https://{request.host}/{location}', 301)
        else:
            return redirect(f'http://{request.host}/{location}', 301)

    # finally, check for TTl matches
    if f"{ontology}/{target}" in ttl:
        location = ttl[f"{ontology}/{target}"]
        if request.is_secure:
            return redirect(f'https://{request.host}/{location}', 301)
        else:
            return redirect(f'http://{request.host}/{location}', 301)

    abort(401)
