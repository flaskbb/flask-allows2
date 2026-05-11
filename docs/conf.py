from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

default_role = "code"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.log_cabinet",
    "sphinx_tabs.tabs",
    "pallets_sphinx_themes",
]

autoclass_style = "both"
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
extlinks = {
    "issue": ("https://github.com/flaskbb/flask-allows2/issues/%s", "#%s"),
    "pr": ("https://github.com/flaskbb/flask-allows2/pull/%s", "#%s"),
    "ghsa": (
        "https://github.com/flaskbb/flask-allows2/security/advisories/GHSA-%s",
        "GHSA-%s",
    ),
}
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}

project = "flask-allows2"
copyright = "2018, Alec Nikolas Reiter; 2026, Peter Justin"
author = "Alec Nikolas Reiter, Peter Justin"
release, version = get_version("flask_allows2")

html_theme = "flask"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("PyPI Releases", "https://pypi.org/project/Flask-Allows2/"),
        ProjectLink("Source Code", "https://github.com/flaskbb/flask-allows2/"),
        ProjectLink(
            "Issue Tracker", "https://github.com/flaskbb/flask-allows2/issues/"
        ),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_title = f"Flask-Allows2 Documentation ({version})"
html_show_sourcelink = False
