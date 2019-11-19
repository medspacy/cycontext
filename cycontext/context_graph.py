class ConTextGraph:

    def __init__(self):
        self.targets = []
        self.modifiers = []
        self.edges = []

    def prune_modifiers(self):
        """Prune overlapping modifiers
        so that only the longest span is kept.
        """
        unpruned = sorted(self.modifiers, key=lambda x: (x.end - x.end))
        if len(unpruned) > 0:
            return self.prune_overlapping_modifiers(unpruned)
        return unpruned

    def prune_overlapping_modifiers(self, modifiers):
        # Don't prune a single modifier
        if len(modifiers) == 1:
            return modifiers

        # Make a copy
        unpruned = list(modifiers)
        pruned = []
        num_mods = len(unpruned)
        curr_mod = unpruned.pop(0)

        while True:
            if len(unpruned) == 0:
                pruned.append(curr_mod)
                break
            if len(unpruned) == 1:
                pruned.append(unpruned.pop(0))
                break
            next_mod = unpruned.pop(0)

            # Check if they overlap
            if curr_mod.overlaps(next_mod):
                # print("Pruning: ", curr_mod, next_mod)
                # Choose the larger
                longer_span = max(curr_mod, next_mod, key=lambda x: (x.end - x.start))
                print(longer_span)
                print()

                pruned.append(longer_span)
                curr_mod = next_mod
            else:
                pruned.append(curr_mod)
                curr_mod = unpruned.pop(0)

        # Recursion base point
        if len(pruned) == num_mods:
            return pruned
        else:
            return self.prune_overlapping_modifiers(pruned)

