# Sphinx configuration for the TwAI Dictionary site.
# The term pages in generated/ are written by tools/build.py; run `make site`.
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
    'source_repository': 'https://github.com/mcdarling/TwAI-Guidelines/',
    'source_branch': 'main',
    'source_directory': 'docs/',
    'light_css_variables': {
        'color-brand-primary': '#1f4e79',
        'color-brand-content': '#1f4e79',
    },
    'dark_css_variables': {
        'color-brand-primary': '#8cb8e6',
        'color-brand-content': '#8cb8e6',
    },
}
