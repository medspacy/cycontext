from spacy import displacy

def visualize_targets(doc, colors=None):
    """Create a NER-style visualization
    for targets and modifiers in Doc."""
    ents_data = []

    modifier_start_chars = set()
    for target in doc.ents:
        ents_data.append({"start": target.start_char, "end":  target.end_char, "label": target.label_})
    for _, modifier in doc._.context_graph.edges:
        if modifier.span.start_char not in modifier_start_chars:
            ents_data.append({"start": modifier.span.start_char, "end": modifier.span.end_char, "label": modifier.category})
            modifier_start_chars.add(modifier.span.start_char)
    ents_data = sorted(ents_data, key=lambda x: x["start"])

    viz_data = [{"text": doc.text,
                "ents": ents_data,
                }]
    if colors is None:
        # TODO: Create a color generator
        colors = dict(CONDITION="orange", DEFINITE_NEGATED_EXISTENCE="#a2bde8")
    options = {"colors": colors,
              }
    displacy.render(viz_data, style="ent", manual=True, options=options)

def visualize_modifiers(doc):
    """Create a dependency-style visualization for
    targets and modifiers in doc."""



    dep_data = {"words": [],
               "arcs": []}

    # TODO: merge phrases together
    token_labels = {}
    for target in doc.ents:
        for i, token in enumerate(target):
            # prefix = "B-" if i == 0 else "I-"
            prefix = ""
            token_labels[token] = prefix+target.label_.upper()
    for target, modifier in doc._.context_graph.edges:
        for i, token in enumerate(modifier.span):
            # prefix = "B-" if i == 0 else "I-"
            prefix = ""
            label = modifier.category.upper()
            # token_labels[token] = prefix+label
            token_labels[token] = ""

        dep_data["arcs"].append(
            {
                "start": min(target.start, modifier.start),
                "end": max(target.start, modifier.start),
                "label": modifier.category,
                "dir": "right" if target > modifier.span else "left"
            }
        )

    dep_data["words"] = [{"text": token.text, "tag": token_labels.get(token, "")} for token in doc]




    displacy.render(dep_data, manual=True)