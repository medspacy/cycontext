# cycontext
A Python implementation of the ConText algorithm for clinical text concept assertion using the spaCy framework

# Overview
This package implements the ConText algorithm within the [spaCy](https://spacy.io) framework. 
[ConText](https://www.sciencedirect.com/science/article/pii/S1532046409000744) detects semantic modifiers such as **negation**, 
**family history**, and **certainty** in clinical text by
relating target concepts (such as "pneumonia") with semantic modifiers (such as "no evidence of"). 

This builds on [pyConText](https://github.com/chapmanbe/pyConTextNLP), which extracts both targets and modifiers using
regular expressions and relates them using a NetworkX graph.

# Key Features
- cycontext is designed to be used as a [spaCy component](https://spacy.io/usage/processing-pipelines)
- It is designed to be modular and not intended to be an end-to-end clinical IE system
- A spaCy pipeline processes one document at a time
- Modifiers are defined in a knowledge base which are used to modify target spans, such as `doc.ents`
- Results are stored in a custom attribute `Doc._.context_graph`

# Basic Usage

```python
import spacy

from cycontext import ConTextComponent, ItemData

nlp = spacy.load("en_core_web_sm")
text = "There is no evidence of pneumonia."

###########################################
# Add code for extracting target concepts #
###########################################


item_data = ItemData("no evidence of", "DEFINITE_NEGATED_EXISTENCE", rule="forward")
context = ConTextComponent([item_data], nlp)
nlp.add_pipe(context, last=True)

doc = nlp(text)

print(doc.ents)
>>> (pneumonia,)

print(doc._.context_graph.edges)
>>> [(pneumonia, <TagObject> [No evidence of, definite_negated_existence])]
```

# Contact Information
Alec Chapman: alec.chapman@hsc.utah.edu