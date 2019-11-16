from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span

from .tag_object import TagObject

class ConTextComponent:
    name = "context"

    def __init__(self, item_data, nlp, attr="ents"):

        """Create a new ConTextComponent algorithm.
        This component matches modifiers in a Doc,
        defines their scope, and identifies edges between targets and modifiers.
        Sets two spaCy extensions:
            - Span._.modifiers: a list of TagObject objects which modify a target Span
            - Doc._.context_graph: a ConText graph object which contains the targets,
                modifiers, and edges between them.

        item_data (list): a list of ItemData objects defining the knowledge base.
        nlp (spacy.lang): a spaCy NLP model
        attr (str): the attribute of Doc which contains targets.
            Default is "ents", in which case it will use the standard Doc.ents attribute.
            Otherwise will look for a custom attribute in Doc._.{attr}

        RETURNS (ConTextComponent)
        """

        self.item_data = item_data
        self.nlp = nlp
        if attr != "ents":
            raise NotImplementedError()
        self.attr = attr


        # _modifier_item_mapping: A mapping from spaCy Matcher match_ids to ItemData
        # This allows us to use spaCy Matchers while still linking back to the ItemData
        # To get the rule and category
        self._modifier_item_mapping = dict()
        self.phrase_matcher = PhraseMatcher(nlp.vocab)
        self.matcher = Matcher(nlp.vocab) # TODO
        for i, item in enumerate(item_data):
            # UID is the hash which we'll use to retrieve the ItemData from a spaCy match
            # And will be a key in self._modifier_item_mapping
            uid = self.nlp.vocab.strings[
                str(i)]
            if item.pattern is None:
                self.phrase_matcher.add(str(i),
                                        None,
                                        nlp(item.literal))
            else:
                raise NotImplementedError()
                # self.matcher.add(str(i),
                #                  None,
                #                  item.pattern)
            self._modifier_item_mapping[uid] = item

        # Set custom attributes
        Span.set_extension("modifiers", default=(), force=True)
        Doc.set_extension("context_edges", default=(), force=True)

    def update_scopes(self, marked_modifiers):
        """For each modifier in a list of TagObjects,
        check against each other modifier to see if one of the modifiers
        should update the other. This allows neighboring similar modifiers
        to extend each other's scope and allows "terminate" modifiers
        to end a modifier's scope.

        marked_modifiers (list): A list of TagObjects in a Doc.
        """
        for i in range(len(marked_modifiers) - 1):
            modifier1 = marked_modifiers[i]
            for j in range(i + 1, len(marked_modifiers)):
                modifier2 = marked_modifiers[j]
                # TODO: Add modifier -> modifier edges
                modifier1.limit_scope(modifier2)
                modifier2.limit_scope(modifier1)

    def apply_modifiers(self, marked_targets, marked_modifiers):
        """Checks each target/modifier pair. If modifier modifies target,
        create an edge between them.

        marked_targets (list): A list of Spans
        marked_modifiers (list): A list of TagObjects

        RETURNS edges (list): A list of tuples consisting of
            target/modifier pairs
        """
        edges = []
        for target in marked_targets:
            for modifier in marked_modifiers:
                if modifier.modifies(target):
                    edges.append((target, modifier))
        return edges

    def __call__(self, doc):
        """Applies the ConText algorithm to a Doc.

        doc (Doc): a spaCy Doc

        RETURNS (Doc)
        """
        if self.attr == "ents":
            targets = doc.ents
        else:
            targets = getattr(doc._, self.attr)
        marked_modifiers = []
        matches = self.phrase_matcher(doc)
        for (match_id, start, end) in matches:
            # Get the ItemData object defining this modifier
            item_data = self._modifier_item_mapping[match_id]
            tag_object = TagObject(item_data, start, end, doc)
            marked_modifiers.append(tag_object)

        self.update_scopes(marked_modifiers)
        edges = self.apply_modifiers(targets, marked_modifiers)
        # TODO: Move to ConText graph
        doc._.context_edges = edges
        for target, modifier in edges:
            target._.modifiers += (modifier,)

        return doc