# Hybrid search

## Reciprocal rank fusion
RRF combines several ranked lists by summing 1 / (k + rank) for each document, with k usually 60.
It uses ranks rather than raw scores because BM25 scores and cosine similarities live on different scales.

## When hybrid helps
Lexical search wins on identifiers and exact names; dense search wins on paraphrases. Fusing both
covers each other's blind spots.
