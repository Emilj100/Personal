# Analysis

## Layer 1, Head 2

This head consistently directs each token’s highest attention weight to the **immediately following** token in the sequence, modeling a “next‑word” pattern.

Example Sentences:
- “The cat sat on the [MASK].” → “The”→“cat”, “cat”→“sat”, …
- “They walked into the [MASK] at dawn.” → “They”→“walked”, “walked”→“into”, “into”→“the”, etc.

## Layer 3, Head 7

This head specializes in the **preposition→object** relationship.

Example Sentences:
- “The cat sat on the [MASK].” → “on”→“[MASK]”
- “They walked into the [MASK] at dawn.” → “into”→“[MASK]”


