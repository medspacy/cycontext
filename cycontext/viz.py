from spacy import displacy

def visualize_ent(doc, colors=None):
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

def visualize_dep(doc):
    """Create a dependency-style visualization for
    targets and modifiers in doc."""
    token_data = []
    token_data_mapping = {}
    for token in doc:
        data = {"text": token.text, "tag": "", "index": token.i}
        token_data.append(data)
        token_data_mapping[token] = data

    # Merge phrases
    targets_and_modifiers = [*doc._.context_graph.targets]
    targets_and_modifiers += [mod.span for mod in doc._.context_graph.modifiers]
    for span in targets_and_modifiers:
        first_token = span[0]
        data = token_data_mapping[first_token]
        data["tag"] = span.label_

        if len(span) == 1:
            continue

        idx = data["index"]
        for other_token in span[1:]:
            # Add the text to the display data for the first word and remove the subsequent token
            data["text"] += " " + other_token.text
            # Remove this token from the list of display data
            token_data.pop(idx + 1)

        # Lower the index of the following tokens
        for other_data in token_data[idx+1:]:
            other_data["index"] -= len(span) - 1

    dep_data = {"words": token_data,
               "arcs": []}
    # Gather the edges between targets and modifiers
    for target, modifier in doc._.context_graph.edges:
        target_data = token_data_mapping[target[0]]
        modifier_data = token_data_mapping[modifier.span[0]]
        dep_data["arcs"].append(
            {
                "start": min(target_data["index"], modifier_data["index"]),
                "end": max(target_data["index"], modifier_data["index"]),
                "label": modifier.category,
                "dir": "right" if target > modifier.span else "left"
            }
        )
    displacy.render(dep_data, manual=True)
    return
