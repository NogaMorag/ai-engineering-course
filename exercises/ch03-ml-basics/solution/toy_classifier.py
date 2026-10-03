"""Chapter 3 solution: a tiny learned classifier for "urgent" support messages.

Run from the course root (as a module, so imports between files work):

    uv run python -m ch03.toy_classifier

The model is deliberately simple: each word gets a weight equal to how much more often it
appears in urgent messages than in non-urgent ones. A message is urgent if the sum of its
word weights is positive. Everything here is standard-library Python.
"""

from __future__ import annotations

import random
import re
from collections import Counter

# (message, is_urgent). Synthetic data written for this exercise.
MESSAGES: list[tuple[str, bool]] = [
    ("The whole site is down and customers cannot log in", True),
    ("Payments are failing for every user since this morning", True),
    ("Production database is not responding", True),
    ("Nobody can access the dashboard, please help now", True),
    ("Our API returns 500 errors on every request", True),
    ("Checkout is broken, we are losing orders every minute", True),
    ("All users are being logged out repeatedly", True),
    ("The service has been unreachable for an hour", True),
    ("Data loss: yesterday's records disappeared", True),
    ("Emails are not being sent to any customer", True),
    ("Login is down for the entire company", True),
    ("Critical: the app crashes on startup for everyone", True),
    ("The outage is affecting all of our stores", True),
    ("Security alert: unknown logins from several accounts", True),
    ("The main page shows an error for every visitor", True),
    ("We cannot process refunds and clients are waiting", True),
    ("Orders are stuck and nothing is shipping", True),
    ("Every upload fails with a timeout", True),
    ("The system deleted invoices by itself", True),
    ("Customers see other customers' data", True),
    ("How do I change the color of my profile picture?", False),
    ("Can you add a dark mode to the settings page?", False),
    ("What is the keyboard shortcut for search?", False),
    ("I would like to export my report as a PDF", False),
    ("Where can I find last month's invoice?", False),
    ("Please update my billing address", False),
    ("Is there a way to rename a project?", False),
    ("The font in the footer looks slightly small", False),
    ("Can I invite a colleague to my workspace?", False),
    ("How do I set up two-factor authentication?", False),
    ("Feature request: sort the list by date", False),
    ("I want to change my notification preferences", False),
    ("What does the yellow icon next to a task mean?", False),
    ("Could you share the API documentation link?", False),
    ("One typo on the pricing page: 'recieve'", False),
    ("Can I schedule a report to run weekly?", False),
    ("How many users does the team plan include?", False),
    ("I forgot how to archive an old project", False),
    ("The tutorial video has no subtitles", False),
    ("Please add my company logo to the invoice template", False),
]

# Very common words carry no signal about urgency; dropping them is a tiny bit of
# "feature engineering" (chapter 3, section 3.1). Real systems use longer lists.
STOP_WORDS = frozenset(
    ["the", "a", "an", "to", "is", "are", "and", "for", "my", "i", "how", "can", "of", "in", "on",
     "we", "our", "do", "you", "it", "with", "this", "that", "be", "as", "by", "from", "please"]
)


def tokenize(text: str) -> list[str]:
    """Lowercase words and numbers, punctuation dropped, stop words removed."""
    return [word for word in re.findall(r"[a-z0-9']+", text.lower()) if word not in STOP_WORDS]


def train(examples: list[tuple[str, bool]]) -> dict[str, float]:
    """Learn one weight per word: how much more often it appears in urgent vs non-urgent messages."""
    urgent_counts: Counter[str] = Counter()
    other_counts: Counter[str] = Counter()
    n_urgent = sum(1 for _, urgent in examples if urgent)
    n_other = len(examples) - n_urgent
    for text, urgent in examples:
        (urgent_counts if urgent else other_counts).update(set(tokenize(text)))
    vocabulary = set(urgent_counts) | set(other_counts)
    # Relative frequency in each class; the difference is the word's weight.
    return {word: urgent_counts[word] / n_urgent - other_counts[word] / n_other for word in vocabulary}


def score(weights: dict[str, float], text: str) -> float:
    return sum(weights.get(word, 0.0) for word in set(tokenize(text)))


def predict(weights: dict[str, float], text: str, threshold: float = 0.0) -> bool:
    return score(weights, text) > threshold


def accuracy(weights: dict[str, float], examples: list[tuple[str, bool]]) -> float:
    correct = sum(predict(weights, text) == urgent for text, urgent in examples)
    return correct / len(examples)


def split(
    examples: list[tuple[str, bool]], held_out: int = 10, seed: int = 42
) -> tuple[list[tuple[str, bool]], list[tuple[str, bool]]]:
    """Shuffle deterministically, then keep `held_out` examples aside for honest measurement."""
    shuffled = examples[:]
    random.Random(seed).shuffle(shuffled)
    return shuffled[held_out:], shuffled[:held_out]


def with_leak(examples: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
    """Append fields that only exist AFTER the ticket was handled: its resolution and queue."""
    return [
        (f"{text} resolution:escalated queue:oncall" if urgent else f"{text} resolution:routine queue:backlog", urgent)
        for text, urgent in examples
    ]


def main() -> None:
    train_set, held_out = split(MESSAGES)
    weights = train(train_set)
    print(f"training examples: {len(train_set)}, held-out examples: {len(held_out)}")
    print(f"accuracy on training data: {accuracy(weights, train_set):.2f}")
    print(f"accuracy on held-out data: {accuracy(weights, held_out):.2f}")

    ranked = sorted(weights.items(), key=lambda item: (-item[1], item[0]))  # ties broken alphabetically: deterministic output
    print("words that push toward urgent:", [word for word, _ in ranked[:6]])
    print("words that push away:        ", [word for word, _ in ranked[-6:]])

    print()
    print("-- the leak --")
    leaked_weights = train(with_leak(train_set))
    print(f"held-out accuracy WITH the leaked fields: {accuracy(leaked_weights, with_leak(held_out)):.2f}")
    print("That number is a lie: resolution and queue are filled in after a human read the")
    print("ticket, so they are never available at prediction time. The model learned to read")
    print("the answer, not the message.")


if __name__ == "__main__":
    main()
