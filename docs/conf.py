# Sphinx configuration for the TwAI Dictionary site.
# The term pages in generated/ are written by tools/build.py; run `make site`.
import os

# The same repository is hosted on GitHub and on GitLab. Point the "view" and
# "edit" links at whichever host is building the site, using the variables
# each CI system sets, and fall back to GitHub for local builds.
if os.environ.get('GITLAB_CI'):
    _repo = os.environ['CI_PROJECT_URL'].rstrip('/')
    _branch = os.environ.get('CI_DEFAULT_BRANCH', 'main')
    _view, _edit = f'{_repo}/-/blob/{_branch}/', f'{_repo}/-/edit/{_branch}/'
else:
    _server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
    _name = os.environ.get('GITHUB_REPOSITORY', 'mcdarling/TwAI-Guidelines')
    _view = f'{_server}/{_name}/blob/main/'
    _edit = f'{_server}/{_name}/edit/main/'
_source = {
    'source_view_link': _view + 'docs/{filename}',
    'source_edit_link': _edit + 'docs/{filename}',
}

# Generated pages are not in the repository, so link them to the file they
# are generated from instead. Pages built from several files get no link.
_GENERATED_FROM = {
    'generated/ai': 'dictionary/ai.yaml',
    'generated/ml': 'dictionary/ml.yaml',
    'generated/trustworthy': 'dictionary/trustworthy.yaml',
    'generated/notes': 'dictionary/notes.yaml',
    'generated/acronyms': 'dictionary/acronyms.yaml',
    'generated/sources': 'references.bib',
}


def _link_generated_pages(app, pagename, templatename, context, doctree):
    if not pagename.startswith('generated/'):
        return
    source = _GENERATED_FROM.get(pagename)
    if source is None:
        context['page_source_suffix'] = ''  # hides both links
    else:
        context['theme_source_view_link'] = _view + source
        context['theme_source_edit_link'] = _edit + source


def setup(app):
    app.connect('html-page-context', _link_generated_pages)


project = 'TwAI Dictionary'
author = 'TwAI Guidelines'
copyright = '2026, TwAI Guidelines'

extensions = ['myst_parser', 'sphinx_design']
myst_enable_extensions = ['attrs_block', 'attrs_inline', 'colon_fence', 'dollarmath']
myst_heading_anchors = 2

exclude_patterns = ['_build', '_extra']
# PDF built by `make pdf`, published at the site root when present.
html_extra_path = ['_extra']

html_theme = 'furo'
html_title = 'TwAI Dictionary'
html_static_path = ['_static']
html_css_files = ['dictionary.css']
html_theme_options = {
    **_source,
    'light_css_variables': {
        'color-brand-primary': '#1f4e79',
        'color-brand-content': '#1f4e79',
    },
    'dark_css_variables': {
        'color-brand-primary': '#8cb8e6',
        'color-brand-content': '#8cb8e6',
    },
}
