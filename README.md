# d3m_ibex - Intelligence Based Entity Xtraction

This primitive is a wrapper for the spaCy named entity recognition tool (https://spacy.io/usage/linguistic-features). Given a text document, `d3m_ibex.get_entities(text, language='english')` will return a list of the named entities detected. A key weakness of spaCy's NER is that it may not recognize proper nouns that are not properly capitalized.

