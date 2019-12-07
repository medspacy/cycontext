"""This module will contain helper functions and classes for common clinical processing tasks
which will be done in conjunction with cycontext.
"""

class PunktSentencizer:
    def __init__(self):
        from nltk.tokenize import PunktSentenceTokenizer
        self.tokenizer = PunktSentenceTokenizer()

    def __call__(self, doc):
        sent_spans = self.tokenizer.span_tokenize(doc.text)
        for token in doc:
            token.is_sent_start = False
        for (start, end) in sent_spans:
            sent = doc.char_span(start, end)
            sent[0].is_sent_start = True
        return doc





class PyRuSHSentencizer:
    def __init__(self, rules_path):
        from PyRuSH.RuSH import RuSH
        self.rules_path = rules_path
        self.rush = RuSH(self.rules_path)

    def __call__(self, doc):
        for token in doc:
            token.is_sent_start = False
        sentence_spans = self.rush.segToSentenceSpans(doc.text)
        for span in sentence_spans:
            sent = doc.char_span(span.begin, span.end)
            sent[0].is_sent_start = True
        return doc
