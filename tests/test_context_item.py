import pytest

from cycontext import ConTextItem
from cycontext.context_item import from_json, from_dict

class TestItemData:

    def test_instantiate1(self):
        literal = "no evidence of"
        category = "DEFINITE_NEGATED_EXISTENCE"
        rule = "forward"
        assert ConTextItem(literal, category, rule)

    def test_context_item_category_upper(self):
        """Test that a ConTextItem category is always upper"""
        literal = "no evidence of"
        category = "definite_negated_existence"
        rule = "forward"
        item = ConTextItem(literal, category, rule)
        assert item.category == "DEFINITE_NEGATED_EXISTENCE"

    def test_context_item_rule_upper(self):
        """Test that a ConTextItem rule is always upper"""
        literal = "no evidence of"
        category = "definite_negated_existence"
        rule = "forward"
        item = ConTextItem(literal, category, rule)
        assert item.rule == "FORWARD"

    def test_rule_value_error(self):
        """Test that ConTextItem raises a ValueError if an invalid rule is passed in."""
        literal = "no evidence of"
        category = "definite_negated_existence"
        rule = "asdf"
        with pytest.raises(ValueError):
            ConTextItem(literal, category, rule)


    def test_from_dict(self):
        d = dict(literal="reason for examination", category="INDICATION", rule="FORWARD")
        assert from_dict(d)

    def test_from_dict_error(self):
        d = dict(literal="reason for examination", category="INDICATION", rule="FORWARD",
                 invalid="this is an invalid key")
        with pytest.raises(ValueError):
            from_dict(d)

    def test_from_json(self, json_file):
        assert from_json(json_file)

@pytest.fixture
def json_file():
    import json, os
    json_filepath = "modifiers.json"

    patterns = [
        {
            "literal": "are ruled out",
            "category": "DEFINITE_NEGATED_EXISTENCE",
            "pattern": None,
            "rule": "backward"
        },
        {
            "literal": "is negative",
            "category": "DEFINITE_NEGATED_EXISTENCE",
            "pattern": [
                {"LEMMA": "be"}, {"LOWER": "negative"}
            ],
            "rule": "backward"
        },
    ]

    # Save dicts to a temporary file
    with open(json_filepath, "w") as f:
        json.dump({"patterns": patterns}, f)

    yield json_filepath
    os.remove(json_filepath)