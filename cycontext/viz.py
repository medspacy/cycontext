from spacy import displacy

def visualize_ent(doc, colors=None):
    """Create a NER-style visualization
    for targets and modifiers in Doc.

    doc (Doc): A spacy doc which has been processed by context
    colors (dict or None): An optional dictionary which maps labels of targets and modifiers
        to color strings to be rendered. If None, will create a generator which
        cycles through the default matplotlib colors.
    """
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
        labels = set()
        for target in doc._.context_graph.targets:
            labels.add(target.label_.upper())
        for modifier in doc._.context_graph.modifiers:
            labels.add(modifier.category.upper())
        colors = _create_color_mapping(labels)
    options = {"colors": colors,
              }
    displacy.render(viz_data, style="ent", manual=True, options=options)

def _create_color_mapping(labels):
    mapping = {}
    color_cycle = _create_color_generator()
    for label in labels:
        if label not in mapping:
            mapping[label] = next(color_cycle)
    return mapping

def _create_color_generator():
    """Create a generator which will cycle through a list of default matplotlib colors"""
    from itertools import cycle
    colors = [u'#1f77b4', u'#ff7f0e', u'#2ca02c', u'#d62728',
              u'#9467bd', u'#8c564b', u'#e377c2', u'#7f7f7f', u'#bcbd22', u'#17becf']
    return cycle(colors)

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
