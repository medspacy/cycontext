import pytest
import spacy

from cycontext import ConTextComponent
from cycontext import ConTextItem
from cycontext.tag_object import TagObject
from cycontext.context_graph import ConTextGraph


nlp = spacy.load("en_core_web_sm")

class TestConTextGraph:

    def context_graph(self):
        doc = nlp("There is no evidence of pneumonia but there is chf.")
        item_data1 = ConTextItem("no evidence of", "DEFINITE_NEGATED_EXISTENCE", "forward")
        tag_object1 = TagObject(item_data1, 2, 5, doc)

        item_data2 = ConTextItem("evidence of", "DEFINITE_EXISTENCE", "forward")
        tag_object2 = TagObject(item_data2, 3, 5, doc)

        item_data3 = ConTextItem("but", "TERMINATE", "TERMINATE")
        tag_object3 = TagObject(item_data3, 6, 7, doc)

        graph = ConTextGraph()
        graph.modifiers = [tag_object1, tag_object2, tag_object3]
        return doc, graph

    def test_init(self):
        assert ConTextGraph()

    def test_apply_modifiers(self):
        doc, graph = self.context_graph()
        graph.targets = [doc[5:6]] # "pneumonia"
        graph.apply_modifiers()
        assert len(graph.edges) == 2

    def test_prune_modifiers(self):
        doc, graph = self.context_graph()
        graph.targets = [doc[5:6]] # "pneumonia"
        graph.prune_modifiers()
        assert len(graph.modifiers) == 2

    def test_update_scopes(self):
        doc, graph = self.context_graph()
        graph.targets = [doc[5:6]]  # "pneumonia"
        graph.apply_modifiers()
        assert graph.modifiers[0].scope == doc[5:]
        graph.update_scopes()
        assert graph.modifiers[0].scope == doc[5:6]

    def test_prune_modifiers_overlap_target(self):
        """Test that a modifier which overlaps with a target is pruned."""
        raise NotImplementedError("Need to write this test.")



