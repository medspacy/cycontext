from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span

from .tag_object import TagObject
from .context_graph import ConTextGraph

#
DEFAULT_ATTRS = {"DEFINITE_NEGATED_EXISTENCE": ("is_experienced", False),
                 "FAMILY_HISTORY": ("is_experienced", False),
                 "INDICATION": ("is_experienced", False),
                 "HISTORICAL": ("is_current", False),
                 }

class ConTextComponent:
    name = "context"

    def __init__(self, nlp, targets="ents", add_attrs=True, prune=True):

        """Create a new ConTextComponent algorithm.
        This component matches modifiers in a Doc,
        defines their scope, and identifies edges between targets and modifiers.
        Sets two spaCy extensions:
            - Span._.modifiers: a list of TagObject objects which modify a target Span
            - Doc._.context_graph: a ConText graph object which contains the targets,
                modifiers, and edges between them.

        nlp (spacy.lang): a spaCy NLP model
        targets (str): the attribute of Doc which contains targets.
            Default is "ents", in which case it will use the standard Doc.ents attribute.
            Otherwise will look for a custom attribute in Doc._.{targets}
        add_attrs (bool): Whether or not to add the additional spaCy Span attributes (ie., Span._.x)
            defining assertion on the targets. By default, these are:
            - is_negated: True if a target is modified by 'DEFINITE_NEGATED_EXISTENCE', default False
            - is_current: False if a target is modified by 'HISTORICAL', default True
            - is_experiencer: False if a target is modified by 'FAMILY_HISTORY', default True
            In the future, these should be made customizable.
        prune (bool): Whether or not to prune modifiers which are substrings of another modifier.
            For example, if "no history of" and "history of" are both ConTextItems, both will match
            the text "no history of afib", but only "no history of" should modify afib.
            If True, will drop shorter substrings completely.
            Default True.

        RETURNS (ConTextComponent)
        """

        self.nlp = nlp
        if targets != "ents":
            raise NotImplementedError()
        self._target_attr = targets
        self.prune = prune

        self._item_data = []
        self._i = 0


        # _modifier_item_mapping: A mapping from spaCy Matcher match_ids to ConTextItem
        # This allows us to use spaCy Matchers while still linking back to the ConTextItem
        # To get the rule and category
        self._modifier_item_mapping = dict()
        self.phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER", validate=True) # TODO: match on custom attributes
        self.matcher = Matcher(nlp.vocab, validate=True)


        self.register_attributes()
        if add_attrs is False:
            self.add_attrs = False
        elif add_attrs is True:
            self.add_attrs = True
            self.context_attributes_mapping = DEFAULT_ATTRS
            Span.set_extension("is_current", default=True, force=True)
            Span.set_extension("is_experienced", default=True, force=True)
        elif isinstance(add_attrs, dict):
            # Check that each of the attributes being added has been set
            for _, (attr_name, _) in add_attrs.items():
                if not Span.has_extension(attr_name):
                    raise ValueError("Custom extension {0} has not been set. Call Span.set_extension.")

            self.add_attrs = True
            self.context_attributes_mapping = add_attrs

        else:
            raise ValueError("add_attrs must be either True (default), False, or a dictionary, not {0}".format(add_attrs))


    @property
    def item_data(self):
        return self._item_data

    def add(self, item_data):
        """Add a list of ConTextItem items to ConText.


        context_item (list)
        """
        self._item_data += item_data

        for item in item_data:

            # UID is the hash which we'll use to retrieve the ConTextItem from a spaCy match
            # And will be a key in self._modifier_item_mapping
            uid = self.nlp.vocab.strings[
                str(self._i)]
            # If no pattern is defined,
            # match on the literal phrase.
            if item.pattern is None:
                self.phrase_matcher.add(str(self._i),
                                        None,
                                        self.nlp.make_doc(item.literal))
            else:
                self.matcher.add(str(self._i),
                                 None,
                                 item.pattern)
            self._modifier_item_mapping[uid] = item
            self._i += 1

    def register_attributes(self):
        """Register spaCy container custom attribute extensions.
        By default will register Span._.modifiers and Doc._.context_graph.

        If self.add_attrs is True, will add additional attributes to span
            as defined in DEFAULT_ATTRS:
            - is_negated
            - is_historical
            - is_experiencer
        """
        Span.set_extension("modifiers", default=(), force=True)
        Doc.set_extension("context_graph", default=None, force=True)


    def set_context_attributes(self, edges):
        """Add Span-level attributes to targets with modifiers.
        """

        for (target, modifier) in edges:
            if modifier.category in self.context_attributes_mapping:
                attr_name, attr_value = self.context_attributes_mapping[modifier.category]
                setattr(target._, attr_name, attr_value)

    def __call__(self, doc):
        """Applies the ConText algorithm to a Doc.

        doc (Doc): a spaCy Doc

        RETURNS (Doc)
        """
        if self._target_attr == "ents":
            targets = doc.ents
        else:
            targets = getattr(doc._, self._target_attr)

        # Store data in ConTextGraph object
        # TODO: move some of this over to ConTextGraph
        context_graph = ConTextGraph()

        context_graph.targets = targets

        context_graph.modifiers = []

        matches = self.phrase_matcher(doc)
        matches += self.matcher(doc)

        # Sort matches
        matches = sorted(matches, key=lambda x:x[1])
        for (match_id, start, end) in matches:
            # Get the ConTextItem object defining this modifier
            item_data = self._modifier_item_mapping[match_id]
            tag_object = TagObject(item_data, start, end, doc)
            context_graph.modifiers.append(tag_object)

        if self.prune:
            context_graph.prune_modifiers()
        context_graph.update_scopes()
        context_graph.apply_modifiers()

        # Link targets to their modifiers
        for target, modifier in context_graph.edges:
            target._.modifiers += (modifier,)

        # If add_attrs is True, add is_negated, is_current, is_asserted to targets
        if self.add_attrs:
            self.set_context_attributes(context_graph.edges)

        doc._.context_graph = context_graph

        return doc