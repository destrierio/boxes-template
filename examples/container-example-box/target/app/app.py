"""
Bulletin — internal announcement composer.

Intentionally vulnerable (CWE-1336, server-side template injection). The
`/preview` endpoint renders the user-supplied `template` field with Jinja2 via
`render_template_string`. A simple denylist blocks common command-execution
gadgets, so the intended solution is to read the flag directly rather than
execute commands.
"""
from flask import Flask, request, render_template_string, Response

app = Flask(__name__)

# Blocks common command-execution gadgets but intentionally allows template expressions to be evaluated
BLOCKLIST = ["popen", "system", "subprocess", "__import__"]

INDEX = """<!doctype html>
<html>
  <head><title>Bulletin</title></head>
  <body>
    <h1>Bulletin</h1>
    <p>Internal announcement composer.</p>
    <p>Compose an announcement with placeholders, then preview it before sending:</p>
    <ul>
      <li><code>POST /preview</code> &mdash; render a draft. form param: <code>template</code></li>
    </ul>
    <p>Example: <code>Hello {{ audience }}, the roadmap review is on Friday.</code></p>
  </body>
</html>
"""


@app.route("/")
def index():
    return INDEX


@app.route("/preview", methods=["POST"])
def preview():
    template = request.form.get("template", "")
    if not template:
        return Response("missing 'template' parameter\n", status=400, mimetype="text/plain")

    lowered = template.lower()
    for bad in BLOCKLIST:
        if bad in lowered:
            return Response("blocked keyword in template\n", status=400, mimetype="text/plain")

    try:
        # VULNERABLE: user-controlled input is rendered as a server-side template (SSTI)
        rendered = render_template_string(template)
        return Response(rendered, mimetype="text/plain")
    except Exception as e:
        return Response(f"template error: {e}\n", status=500, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)