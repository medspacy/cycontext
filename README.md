# cycontext
A Python implementation of the ConText algorithm for clinical text concept assertion using the spaCy framework.

# This package is deprecated!
Development for `cycontext` has been moved to [medSpaCy](https://github.com/medspacy/medspacy) and should now be installed as:

```bash
pip install medspacy
```

```python
# Option 1: Load with a medspacy pipeline
import medspacy
nlp = medspacy.load()
print(nlp.pipe_names)

# Option 2: Manually add to a spaCy model
import spacy
from medspacy.context import ConTextComponent
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(ConTextComponent(nlp))
```
[<img src="https://github.com/medspacy/medspacy/raw/master/images/medspacy_logo.png" align="center">](https://github.com/medspacy/medspacy)

Please see the [medSpaCy](https://github.com/medspacy/medspacy) GitHub page for additional information and documentation.
