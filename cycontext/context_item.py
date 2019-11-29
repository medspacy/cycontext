class ConTextItem:
    """An ConTextItem defines a ConText modifier. It defines the phrase to be matched,
    the category/semantic class, and the rule which the modifier executes.
    """
    _ALLOWED_RULES = ("FORWARD", "BACKWARD", "BIDIRECTIONAL", "TERMINATE")
    def __init__(self, literal, category, rule="BIDIRECTIONAL", pattern=None, comment=''):
        """Create an ConTextItem object.

        literal (str): The actual string of a concept. If pattern is None,
            this string will be matched exactly.
        category (str): The semantic class of the item.
        pattern (list or None): A spaCy pattern to match using token attributes.
            See https://spacy.io/usage/rule-based-matching.
        rule (str): The directionality or action of a modifier.
            One of ("forward", "backward", "bidirectional", or "terminate").
        RETURNS (ConTextItem)
        """
        self.literal = literal
        self.category = category.upper()
        self.pattern = pattern
        self.rule = rule.upper()
        self.comment = comment

        if self.rule not in self._ALLOWED_RULES:
            raise ValueError("Rule {0} not recognized. Must be one of: {1}".format(self.rule, self._ALLOWED_RULES))

    def __repr__(self):
        return f"ConTextItem: [{self.literal}, {self.category}, {self.pattern}, {self.rule}]"

ALLOWED_KEYS = {"rule", "pattern", "category", "pattern", "comment"}

def from_json(filepath):
    """Read in a lexicon of modifiers from a JSON file.

    filepath (text): the .json file containing modifier rules

    RETURNS item_data (list): a list of ConTextItem objects
    RAISES KeyError if the dictionary contains any keys other than
        those accepted by ConTextItem.__init__
    """
    import json
    with open(filepath) as f:
        modifier_data = json.load(f)
    item_data = []
    for data in modifier_data["patterns"]:
        item_data.append(from_dict(data))
    return item_data

def from_dict(d):
    try:
        item = ConTextItem(**d)  # TODO: this will throw an error if there are any erroneous keys
    except TypeError:
        keys = set(d.keys())
        invalid_keys = keys.difference(ALLOWED_KEYS)
        msg = ("JSON object contains invalid keys: {0}.\n"
              "Must be one of: {1}".format(invalid_keys, ALLOWED_KEYS))
        raise ValueError(msg)

    return item