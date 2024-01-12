# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'absbox'
copyright = '2024, Xiaoyu Zhang'
author = 'Xiaoyu Zhang'

release = '0.23.4'
version = '0.23.4'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinxemoji.sphinxemoji',
    'sphinx.ext.graphviz'
    #'nbsphinx'
    #'myst_nb'
]

graphviz_output_format = 'svg'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}

html_theme_options = {
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 5,
    'includehidden': True,
    'titles_only': False    
}


intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
