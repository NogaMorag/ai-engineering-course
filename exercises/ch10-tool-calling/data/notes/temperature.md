# Temperature and sampling

Temperature divides the logits before softmax. Low temperature sharpens the distribution and makes
the model pick the same continuation almost every time; high temperature flattens it and adds variety.
Temperature zero is not "truth mode": a wrong answer just becomes a consistently wrong answer.
Seeds make repeats likely identical, not guaranteed.
