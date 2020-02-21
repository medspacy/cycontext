from os import path

from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span

from .tag_object import TagObject
from .context_graph import ConTextGraph
from .context_item import ConTextItem

#
DEFAULT_ATTRS = {"DEFINITE_NEGATED_EXISTENCE": ("is_experienced", False),
                 "FAMILY_HISTORY": ("is_experienced", False),
                 "INDICATION": ("is_experienced", False),
                 "HISTORICAL": ("is_current", False),
                 }

class ConTextComponent:
    name = "context"

    def __init__(self, nlp, targets="ents", add_attrs=True, prune=True, rules='default', rule_list=None):

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
        rules (str): Which rules to load on initialization. Default is 'default'.
            - 'default': Load the default set of rules provided with cyConText
            - 'other': Load a custom set of rules, please also set _______ with a file path or list.
            - None: Load no rules.
        rule_list (str or list): The location of rules in json format or a list of ContextItems. Default
            is None.


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

        if rules == 'default':
            # use a default rule list, pneumonia for testing
            self._item_data = ConTextItem.from_json("./kb/default_rules.json")

        elif rules == 'other':
            # use custom rules
            if isinstance(rule_list, str):
                # if rules_list is a string, then it must be a path to a json
                if path.exists(rule_list):
                    self._item_data = ConTextItem.from_json(rule_list)
                else:
                    raise ValueError("rule_list must be a valid path. Currently is: {0}".format(rule_list))

            elif isinstance(rule_list, list):
                # otherwise it is a list of contextitems
                if not rule_list:
                    raise ValueError("rule_list must not be empty.")
                for item in rule_list:
                    # check that all items are contextitems
                    if not isinstance(item, ConTextItem):
                        raise ValueError("rule_list must contain only ContextItems. Currently contains: {0}".format(type(item)))
                self._item_data = rule_list

            else:
                raise ValueError("rule_list must be a valid path or list of ContextItems. Currenty is: {0}".format(type(rule_list)))

        elif not rules: 
            # otherwise leave the list empty.
            # do nothing
            self._item_data = []

        else:
            # loading from json path or list is possible later
            raise ValueError("rules must either be 'default' (default), 'other' or None.")


    @property
    def item_data(self):
        return self._item_data

    def add(self, item_data):
        """Add a list of ConTextItem items to ConText.


        context_item (list)
        """
        try:
            self._item_data += item_data
        except TypeError:
            raise TypeError("item_data must be a list of ConText items. If you're just passing in a single ConText Item, "
                            "make sure to wrap the item in a list: `context.add([item])`")

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
