class TagObject:
    """Represents a concept found by ConText in a document.
    Is the result of ItemData matching a span of text in a Doc.
    """

    def __init__(self, item_data, start, end, doc):
        """Create a new TagObject from a document span.

        item_data (int): The ItemData object which defines the modifier.
        start (int): The start token index.
        end (int): The end token index (non-inclusive).
        doc (Doc): The spaCy Doc which contains this span.
        """
        self.item_data = item_data
        self.start = start
        self.end = end
        self.doc = doc

        self._scope_start = None
        self._scope_end = None
        self.set_scope()

    @property
    def span(self):
        """The spaCy Span object, which is a view of self.doc, covered by this match."""
        return self.doc[self.start: self.end]

    @property
    def rule(self):
        return self.item_data.rule

    @property
    def category(self):
        return self.item_data.category

    @property
    def scope(self):
        return self.doc[self._scope_start: self._scope_end]

    def set_scope(self):
        """Applies the rule of the ItemData which generated
        this TagObject to define a scope in the sentence.
        For example, if the rule is "forward", the scope will be [self.end: sentence.end].
        If the rule is "backward", it will be [self.start: sentence.start].
        """
        sent = self.doc[self.start].sent

        if self.rule.lower() == "forward":
            self._scope_start, self._scope_end = self.end, sent.end
        elif self.rule.lower() == "backward":
            self._scope_start, self._scope_end = sent.start, self.start
        else:
            self._scope_start, self._scope_end = sent.start, sent.end

    def update_scope(self, span):
        """Change the scope of self to be the given spaCy span.

        span (Span): a spaCy Span which contains the scope
        which a modifier should cover.
        """
        self._scope_start, self._scope_end = span.start, span.end

    def limit_scope(self, other):
        """If self and obj have the same category
        or if obj has a directionality of 'terminate',
        use the span of obj to update the scope of self.

        other (TagObject)
        Returns True if obj modfified the scope of self
        """
        if self.span.sent != other.span.sent:
            return False
        if self.rule.lower() == "terminate":
            return False
        if other.rule.lower() not in ("terminate", self.rule.lower()):
            return False

        orig_scope = self.scope

        if (self.rule.lower() in ("forward", "bidirectional")):
            if other > self:
                self._scope_end = min(self._scope_end, other.start)
        elif (self.rule.lower() in ("backward", "bidirectional")):
            if other < self:
                self._scope_start = max(self._scope_start, other.end)
        if orig_scope != self.scope:
            return True
        else:
            return False

    def modifies(self, target):
        """Returns True if the target is within the modifier scope.

        target (Span): a spaCy span representing a target concept.
        """
        if self.rule == "terminate":
            return False
        if target[0] in self.scope:
            return True
        if target[-1] in self.scope:
            return True
        return False

    def __gt__(self, other):
        return self.span > other.span

    def __ge__(self, other):
        return self.span >= other.span

    def __lt__(self, other):
        return self.span < other.span

    def __le__(self, other):
        return self.span <= other.span

    def __repr__(self):
        return f"<TagObject> [{self.span}, {self.category}]"