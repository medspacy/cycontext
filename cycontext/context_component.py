from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span

from .tag_object import TagObject
from .context_graph import ConTextGraph
from nltk.tokenize import PunktSentenceTokenizer

class ConTextComponent:
    name = "context"

    def __init__(self, nlp, attr="ents"):

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

        self.nlp = nlp
        if attr != "ents":
            raise NotImplementedError()
        self.attr = attr
        # self.tokenizer = PunktSentenceTokenizer() # TODO: can we avoid this?

        self._item_data = []
        self._i = 0


        # _modifier_item_mapping: A mapping from spaCy Matcher match_ids to ItemData
        # This allows us to use spaCy Matchers while still linking back to the ItemData
        # To get the rule and category
        self._modifier_item_mapping = dict()
        self.phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER", validate=True) # TODO: match on custom attributes
        self.matcher = Matcher(nlp.vocab, validate=True)


        # TODO: Think of a smarter way to do this
        Span.set_extension("modifiers", default=(), force=True)
        Doc.set_extension("context_graph", default=None, force=True)

    @property
    def item_data(self):
        return self._item_data

    def add(self, item_data):
        """Add a list of ItemData items to ConText.


        item_data (list)
        """
        self._item_data += item_data

        for item in item_data:

            # UID is the hash which we'll use to retrieve the ItemData from a spaCy match
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


    def __call__(self, doc):
        """Applies the ConText algorithm to a Doc.

        doc (Doc): a spaCy Doc

        RETURNS (Doc)
        """
        if self.attr == "ents":
            targets = doc.ents
        else:
            targets = getattr(doc._, self.attr)

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
            # Get the ItemData object defining this modifier
            item_data = self._modifier_item_mapping[match_id]
            tag_object = TagObject(item_data, start, end, doc)
            context_graph.modifiers.append(tag_object)

        context_graph.prune_modifiers()

        # TODO: This should be the context graph
        context_graph.update_scopes()
        context_graph.edges = context_graph.apply_modifiers()

        # Link targets to their modifiers
        for target, modifier in context_graph.edges:
            target._.modifiers += (modifier,)

        doc._.context_graph = context_graph

        return doc