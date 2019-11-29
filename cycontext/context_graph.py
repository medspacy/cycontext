class ConTextGraph:

    def __init__(self):
        self.targets = []
        self.modifiers = []
        self.edges = []


    def update_scopes(self):
        """For each modifier in a list of TagObjects,
        check against each other modifier to see if one of the modifiers
        should update the other. This allows neighboring similar modifiers
        to extend each other's scope and allows "terminate" modifiers
        to end a modifier's scope.

        marked_modifiers (list): A list of TagObjects in a Doc.
        """
        for i in range(len(self.modifiers) - 1):
            modifier1 = self.modifiers[i]
            for j in range(i + 1, len(self.modifiers)):
                modifier2 = self.modifiers[j]
                # TODO: Add modifier -> modifier edges
                modifier1.limit_scope(modifier2)
                modifier2.limit_scope(modifier1)

    def apply_modifiers(self):
        """Checks each target/modifier pair. If modifier modifies target,
        create an edge between them.

        marked_targets (list): A list of Spans
        marked_modifiers (list): A list of TagObjects

        RETURNS edges (list): A list of tuples consisting of
            target/modifier pairs
        """
        edges = []
        for target in self.targets:
            for modifier in self.modifiers:
                if modifier.modifies(target):
                    edges.append((target, modifier))
        self.edges = edges

    def prune_modifiers(self):
        """Prune overlapping modifiers
        so that only the longest span is kept.
        """
        unpruned = sorted(self.modifiers, key=lambda x: (x.end - x.end))
        if len(unpruned) > 0:
            rslt = self.prune_overlapping_modifiers(unpruned)
            self.modifiers = rslt

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
            # if len(unpruned) == 1:
            #     pruned.append(unpruned.pop(0))
            #     break
            next_mod = unpruned.pop(0)

            # Check if they overlap
            if curr_mod.overlaps(next_mod):
                # Choose the larger
                longer_span = max(curr_mod, next_mod, key=lambda x: (x.end - x.start))

                pruned.append(longer_span)
                if len(unpruned) == 0:
                    break
                curr_mod = unpruned.pop(0)
            else:
                pruned.append(curr_mod)
                curr_mod = next_mod
        # Recursion base point
        if len(pruned) == num_mods:
            return pruned
        else:
            return self.prune_overlapping_modifiers(pruned)

    def __repr__(self):
        return "<ConTextGraph> with {0} targets and {1} modifiers".format(len(self.targets), len(self.modifiers))

