import pytest
import spacy

from cycontext import ConTextItem
from cycontext.tag_object import TagObject

nlp = spacy.load("en_core_web_sm")

class TestTagObject:

    def create_objects(self):
        doc = nlp("family history of breast cancer but no diabetes. She has afib.")
        item = ConTextItem("family history of", "FAMILY_HISTORY", rule="FORWARD")
        tag_object = TagObject(item, 0, 3, doc)
        return doc, item, tag_object

    def test_init(self):
        assert self.create_objects()

    def test_span(self):
        doc, item, tag_object = self.create_objects()
        assert tag_object.span == doc[0:3]

    def test_set_span_fails(self):
        doc, item, tag_object = self.create_objects()
        with pytest.raises(AttributeError):
            tag_object.span = "Can't do this!"

    def test_rule(self):
        doc, item, tag_object = self.create_objects()
        assert tag_object.rule == "FORWARD"

    def test_category(self):
        doc, item, tag_object = self.create_objects()
        assert tag_object.category == "FAMILY_HISTORY"

    def test_default_scope(self):
        """Test that the scope goes from the end of the modifier phrase
        to the end of the sentence.
        """
        doc, item, tag_object = self.create_objects()
        assert tag_object.scope == doc[3:-4]

    def test_limit_scope(self):
        """Test that a 'TERMINATE' TagObject limits the scope of the tag object"""
        doc, item, tag_object = self.create_objects()
        item2 = ConTextItem("but", "TERMINATE", "TERMINATE")
        tag_object2 = TagObject(item2, 2, 4, doc)
        assert tag_object.limit_scope(tag_object2)

    def test_limit_scope2(self):
        doc, item, tag_object = self.create_objects()
        item2 = ConTextItem("but", "TERMINATE", "TERMINATE")
        tag_object2 = TagObject(item2, 2, 4, doc)
        assert not tag_object2.limit_scope(tag_object)

    def test_update_scope(self):
        doc, item, tag_object = self.create_objects()
        tag_object.update_scope(doc[3:5])

    def test_modifies(self):
        """Test that the TagObject modifies a target in its scope"""
        doc, item, tag_object = self.create_objects()
        assert tag_object.modifies(doc[3:5])

    def test_not_modifies(self):
        """Test that the TagObject does not modify a target outside of its scope"""
        doc, item, tag_object = self.create_objects()
        assert not tag_object.modifies(doc[-2:])

    def test_context_item(self):
        doc, item, tag_object = self.create_objects()
        assert tag_object.context_item is item




