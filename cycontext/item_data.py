class ItemData:
    """An ItemData defines a ConText modifier. It defines the phrase to be matched,
    the category/semantic class, and the rule which the modifier executes.
    """
    _ALLOWED_RULES = ("forward", "backward", "bidirectional", "terminate")
    def __init__(self, literal, category, pattern=None, rule="bidirectional"):
        """Create an ItemData object.

        literal (str): The actual string of a concept. If pattern is None,
            this string will be matched exactly.
        category (str): The semantic class of the item.
        pattern (list or None): A spaCy pattern to match using token attributes.
            See https://spacy.io/usage/rule-based-matching.
        rule (str): The directionality or action of a modifier.
            One of ("forward", "backward", "bidirectional", or "terminate").
        RETURNS (ItemData)
        """
        self.literal = literal
        self.category = category.lower()
        self.pattern = pattern
        self.rule = rule.lower()

        if self.rule not in self._ALLOWED_RULES:
            raise ValueError("Rule {0} not recognized. Must be one of: {1}".format(self.rule, self._ALLOWED_RULES))

    def __repr__(self):
        return f"ItemData: [{self.literal}, {self.category}, {self.pattern}, {self.rule}]"