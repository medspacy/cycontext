class ConTextItem:
    """An ConTextItem defines a ConText modifier. It defines the phrase to be matched,
    the category/semantic class, and the rule which the modifier executes.
    """
    _ALLOWED_RULES = ("FORWARD", "BACKWARD", "BIDIRECTIONAL", "TERMINATE")
    _ALLOWED_KEYS = {"literal", "rule", "pattern", "category", "metadata"}
    def __init__(self, literal, category, rule="BIDIRECTIONAL", pattern=None, metadata=None):
        """Create an ConTextItem object.

        literal (str): The actual string of a concept. If pattern is None,
            this string will be lower-cased and matched to the lower-case string.
        category (str): The semantic class of the item.
        pattern (list or None): A spaCy pattern to match using token attributes.
            See https://spacy.io/usage/rule-based-matching.
        rule (str): The directionality or action of a modifier.
            One of ("forward", "backward", "bidirectional", or "terminate").
        metadata (dict or None): A dict of additional data to pass in,
            such as free-text comments, additional attributes, or ICD-10 codes.
            Default None.
        RETURNS (ConTextItem)
        """
        self.literal = literal.lower()
        self.category = category.upper()
        self.pattern = pattern
        self.rule = rule.upper()
        self.metadata = metadata

        if self.rule not in self._ALLOWED_RULES:
            raise ValueError("Rule {0} not recognized. Must be one of: {1}".format(self.rule, self._ALLOWED_RULES))

    @classmethod
    def from_json(cls, filepath):
        """Read in a lexicon of modifiers from a JSON file.

        filepath (text): the .json file containing modifier rules

        RETURNS context_item (list): a list of ConTextItem objects
        RAISES KeyError if the dictionary contains any keys other than
            those accepted by ConTextItem.__init__
        """
        import json
        with open(filepath) as f:
            modifier_data = json.load(f)
        item_data = []
        for data in modifier_data["item_data"]:
            item_data.append(ConTextItem.from_dict(data))
        return item_data

    @classmethod
    def from_dict(cls, d):
        try:
            item = ConTextItem(**d)
        except TypeError:
            keys = set(d.keys())
            invalid_keys = keys.difference(cls._ALLOWED_KEYS)
            msg = ("JSON object contains invalid keys: {0}.\n"
                   "Must be one of: {1}".format(invalid_keys, cls._ALLOWED_KEYS))
            raise ValueError(msg)

        return item

    @classmethod
    def to_json(cls, item_data, filepath):
        import json
        data = {"item_data": [item.to_dict() for item in item_data]}
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    def to_dict(self):
        d = {}
        for key in self._ALLOWED_KEYS:
            d[key] = self.__dict__[key]
        return d

    def __repr__(self):
        return f"ConTextItem(literal='{self.literal}', category='{self.category}', pattern={self.pattern}, rule='{self.rule}')"




