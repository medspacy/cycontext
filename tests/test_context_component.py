import spacy

from cycontext import ConTextComponent
from cycontext import ConTextItem



nlp = spacy.load("en_core_web_sm")

class TestConTextComponent:

    def test_initiate(self):
        assert ConTextComponent(nlp)

    def test_call(self):
        doc = nlp("Pulmonary embolism has been ruled out.")
        context = ConTextComponent(nlp)
        doc = context(doc)
        assert isinstance(doc, spacy.tokens.doc.Doc)

    def test_registers_attributes(self):
        """Test that the default ConText attributes are set on ."""
        doc = nlp("There is consolidation.")
        doc.ents = (doc[-2:-1], )
        context = ConTextComponent(nlp)
        doc = context(doc)
        assert hasattr(doc._, "context_graph")
        assert hasattr(doc.ents[0]._, "modifiers")

    def test_registers_context_attributes(self):
        """Test that the additional attributes such as
        'is_negated' are registered on spaCy spans.
        """
        doc = nlp("This is a span.")
        context = ConTextComponent(nlp, add_attrs=True)
        context(doc)
        span = doc[-2:]
        assert hasattr(span._, "is_current")
        assert hasattr(span._, "is_experienced")

    def test_default_attribute_values(self):
        doc = nlp("There is evidence of pneumonia.")
        context = ConTextComponent(nlp, add_attrs=True)
        doc.ents = (doc[-2:-1],)
        context(doc)

        assert doc.ents[0]._.is_current is True
        assert doc.ents[0]._.is_experienced is True

    def test_is_negated(self):
        doc = nlp("There is no evidence of pneumonia.")
        context = ConTextComponent(nlp, add_attrs=True)
        item_data = [ConTextItem("no evidence of", "DEFINITE_NEGATED_EXISTENCE", rule="forward")]
        context.add(item_data)
        doc.ents = (doc[-2:-1],)
        context(doc)

        assert doc.ents[0]._.is_experienced is False

    def test_is_current(self):
        doc = nlp("History of pneumonia.")
        context = ConTextComponent(nlp, add_attrs=True)
        item_data = [ConTextItem("history of", "HISTORICAL", rule="forward")]
        context.add(item_data)
        doc.ents = (doc[-2:-1],)
        context(doc)

        assert doc.ents[0]._.is_current is False

    def test_is_experienced(self):
        doc = nlp("Family history of breast cancer.")
        context = ConTextComponent(nlp, add_attrs=True)
        item_data = [ConTextItem("family history of", "FAMILY_HISTORY", rule="forward")]
        context.add(item_data)
        doc.ents = (doc[-3:-1],)
        context(doc)

        assert doc.ents[0]._.is_experienced is False

    def test_custom_attributes(self):
        raise NotImplementedError()
