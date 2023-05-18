# main.py
from flask import Flask, send_file, request, Response, jsonify, abort
from flask_cors import CORS
import os
import requests
import logging
import arxiv  # Import the arxiv library

# Configurate application
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route("/logo.png", methods=['GET'])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json", methods=['GET'])
def plugin_manifest():
    host = request.headers['Host']
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="application/json")

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

@app.route("/search", methods=['POST'])
def search_papers():
    data = request.get_json()
    if data is None or 'query' not in data:
        abort(400, description="Bad Request: 'query' is required.")
    query = data['query']
    # Search for papers on arXiv
    arxivClient = arxiv.Client(
        page_size = 5,
        delay_seconds = 3,
        num_retries = 3
    )
    searchQuery = arxiv.Search(
        query = query,
        max_results = 5,
        sort_by = arxiv.SortCriterion.SubmittedDate
        )
    papers = []
    logging.info(f'Query income: \"{query}\"')

    for paper in arxivClient.results(searchQuery):
        papers.append({
            'id': paper.entry_id,
            'published': paper.published,
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'primary_category': paper.primary_category,
            'pdf_url': paper.pdf_url
        })
        logging.info(f'Paper found: \"{paper.title}\"')
    return jsonify({'status': 'success', 'papers': papers}), 200

def main():
    app.run(debug=False, host="0.0.0.0", port=5004)

if __name__ == "__main__":
    main()
