---
tags: [sample]
---
# Sampling and temperature

## What temperature does
Temperature divides the logits before the softmax. A low temperature sharpens the distribution, so the
same continuation wins almost every time; a high temperature flattens it and adds variety.

## What temperature does not do
Temperature zero is not a truth mode. A wrong answer simply becomes a consistently wrong answer.
Seeds make repeated runs likely identical, not guaranteed.
