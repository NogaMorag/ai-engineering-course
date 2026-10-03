# Decision memo: the newsletter summaries cite facts that are not in the article

**Observed failure.** In the dev eval, 4 of 20 summaries contain a claim that does not appear in the source
(faithfulness judge: false; failure type: unsupported_answer).

**Evidence.** `results/dev-v2.jsonl`, cases c07, c11, c14, c19. All four articles are short (under 120 words);
the model fills the three-bullet shape with background knowledge.

**Decision.** Keep the schema; add an `is_article` style escape for thin sources ("fewer than three facts" ->
two bullets allowed) and tighten the prompt ("use only facts that appear in the article"). Not RAG: the
missing facts are not missing, the model is adding facts; the fix is specification, not retrieval.

**Alternatives considered.** RAG over the publisher's site (adds cost and a crawler for a problem that is not
missing information). A smarter model (hides the specification gap at five times the price).

**Cost.** One afternoon; zero per-call cost change.

**Risks.** Two-bullet summaries look thinner; measured by the reader (me) for a week.

**How we will know.** The faithfulness judge on the same 20 cases: 4 unsupported -> at most 1, with no drop in
the "valid" column. Re-run on holdout once.
