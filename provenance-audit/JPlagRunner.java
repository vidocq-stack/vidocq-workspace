/*
 * Copyright (c) 2026 Yann Blazart, Antoine Sabot-Durand and the Vidocq contributors
 *
 * SPDX-License-Identifier: EPL-2.0 OR EUPL-1.2 OR GPL-2.0-or-later
 */

import de.jplag.JPlag;
import de.jplag.JPlagComparison;
import de.jplag.java.JavaLanguage;
import de.jplag.options.JPlagOptions;

import java.io.File;
import java.util.Set;

/**
 * Pass 3 of the provenance audit: structural similarity between one Vidocq brick and the
 * reference implementation of the same specification.
 *
 * <p>Where CPD compares raw token windows, JPlag parses both corpora into a language-aware
 * token stream and runs Greedy String Tiling over it. That survives renaming, reordering,
 * reformatting and moderate restructuring — the transformations that hide a copy from CPD.
 * It is the answer to limit 1 recorded in {@code PROVENANCE-AUDIT.md} §5.</p>
 *
 * <p>Reads a staging directory holding exactly two submissions ({@code vidocq/} and
 * {@code ri/}) and prints one line per comparison, plus the largest matched fragment.
 * Run through {@code jplag.sh}, which builds the staging directories.</p>
 *
 * <pre>
 *   java -cp "$(cat cp.txt):." JPlagRunner &lt;stagingDir&gt; &lt;minTokenMatch&gt; &lt;label&gt;
 * </pre>
 */
public final class JPlagRunner {

    public static void main(String[] args) throws Exception {
        var staging = new File(args[0]);
        var minTokens = Integer.parseInt(args[1]);
        var label = args[2];

        var options = new JPlagOptions(new JavaLanguage(), Set.of(staging), Set.of())
                .withMinimumTokenMatch(minTokens)
                // Report every comparison: a similarity threshold would hide precisely the
                // low-but-non-zero scores this audit needs to look at.
                .withSimilarityThreshold(0.0);

        try {
            var result = JPlag.run(options);
            var comparisons = result.getAllComparisons();
            if (comparisons.isEmpty()) {
                System.out.printf("%-13s %8s %10s  %s%n", label, "-", "-", "aucune comparaison");
                return;
            }
            for (JPlagComparison c : comparisons) {
                var longest = c.matches().stream().mapToInt(m -> m.length()).max().orElse(0);
                System.out.printf("%-13s %7.2f%% %10d  plus long fragment: %d tokens  (%s vs %s)%n",
                        label,
                        c.similarity() * 100,
                        c.getNumberOfMatchedTokens(),
                        longest,
                        c.firstSubmission().getName(),
                        c.secondSubmission().getName());
            }
        } catch (Exception e) {
            System.out.printf("%-13s %8s %10s  ERREUR: %s%n", label, "-", "-", e);
        }
    }
}
