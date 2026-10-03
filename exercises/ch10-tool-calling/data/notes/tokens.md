# Tokens

The model reads tokens, not words. Prices and context limits are counted in tokens.
Hebrew costs more tokens than English for the same meaning, so count with the model's own counter
instead of guessing from word counts.
Output tokens are the slow part of a request: they are generated one at a time.
