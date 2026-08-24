# RAG Concept Session — Notes

These notes cover the core concepts behind a RAG (Retrieval-Augmented Generation) pipeline: embeddings, cosine similarity, chunking, the full RAG flow, hallucination, and source attribution. They are written as a foundation before building a library-free mini RAG by hand.

---

## 1. Embedding

An embedding is **text turned into a list of numbers (a vector)** that represents its *meaning*.

**Why we do this:** Computers can't compare meaning directly — they can't "read." But they *can* compare numbers. So each piece of text is converted into numbers, positioned so that **similar meanings end up with similar numbers**.

**The intuition:** Imagine a map where every piece of text is a point.
- "annual leave" and "vacation days" land **close together** (similar meaning)
- "annual leave" and "VPN setup" land **far apart** (unrelated)

An embedding is just the **coordinates** of that point.

**Tiny example** (real embeddings have hundreds of numbers, but imagine just 3):

```
"leave days"   → [0.9, 0.1, 0.2]
"vacation"     → [0.8, 0.2, 0.1]   ← close to "leave days"
"VPN setup"    → [0.1, 0.9, 0.7]   ← far away
```

The first two have similar numbers; the third is different. That closeness is what gets measured next, with cosine similarity.

**Key point:** The numbers themselves are meaningless to read. What matters is the **relative distance** between them — that's what captures meaning.

> Note: This is a simplified teaching model. Real embeddings come from trained neural networks, but the "text → meaningful coordinates" intuition is exactly right.

---

## 2. Cosine Similarity

Once text is turned into vectors, there needs to be a way to measure **how close two vectors are** in meaning. Cosine similarity is that measuring tool.

**The core idea:** It measures the **angle** between two vectors, not their length.
- **Small angle** (vectors point the same way) → very similar → score near **1**
- **90° angle** (unrelated directions) → score near **0**
- **Opposite directions** → score near **-1**

**Why angle, not distance:** Meaning is about **direction**, not size. A short text and a long text about the same topic point the *same way* even if one vector is "bigger." Cosine ignores length and looks only at direction — so it captures topic similarity cleanly.

**Visual intuition:**

```
   ↑ "vacation"
   |  ╱ "leave days"      ← small angle → high similarity
   | ╱
   |╱________→ "VPN setup"  ← ~90° → low similarity
```

**The formula:**

```
cosine_similarity(A, B) = (A · B) / (|A| × |B|)
```

- `A · B` = dot product (multiply matching numbers, sum them)
- `|A|`, `|B|` = length (magnitude) of each vector
- No libraries needed — it's just multiplication, addition, and a square root

**In the RAG pipeline:** Compute cosine similarity between the **question's vector** and **each chunk's vector**, then pick the chunk with the **highest score**. That's the "find the closest chunk" step.

---

## 3. Chunking

Chunking is **splitting a document into smaller pieces ("chunks")** before embedding each one.

**Why not embed the whole document:**

1. **Precision.** Embedding a whole multi-paragraph document as one vector produces one blurry average of everything in it. When a question matches only one sentence, the goal is to return *that part* — not the entire document. Smaller chunks = sharper matches.

2. **Context limits.** Later, chunks get fed to the LLM, which has a size limit. Chunks keep what gets sent small and relevant.

**The trade-off (this is the real skill):**

| Chunk size | Effect |
|-----------|--------|
| **Too big** | Blurry match, includes irrelevant text |
| **Too small** | Loses context, meaning gets fragmented |

Finding the right size is why chunking *strategy* matters.

**Common ways to chunk:**
- **By paragraph** — natural, simple
- **By sentence** — finer, more precise
- **Fixed size** (e.g. every 200 words) — often with slight **overlap** so meaning isn't cut mid-thought

**A simple starting approach:** Chunk by paragraph or by sentence. Documents with clear paragraphs can be split on blank lines cleanly.

**Example:** A leave-policy document with 3 paragraphs becomes 3 chunks. The question "How many leave days?" should match the **first chunk** (the one mentioning the number of days), not the whole file.

---

## 4. The RAG Flow

How every piece connects:

```
Question → Embedding → Similarity Search → Context → LLM → Answer
```

**Step by step:**

1. **Question** — A user asks: *"How many leave days do I have?"*
2. **Embedding** — Turn the question into a vector, using the same method applied to the chunks, so they're comparable.
3. **Similarity search** — Compute cosine similarity between the question's vector and **every chunk's** vector. Rank them. Pick the highest — the closest chunk.
4. **Context** — Take that winning chunk (the leave-policy text). This becomes the **context** handed to the LLM.
5. **LLM** — Send the LLM the *question* + the *retrieved chunk*. The prompt is essentially: "Using this context, answer the question."
6. **Answer** — The LLM replies using the provided context: *"You have 14 days of annual leave."*

**The key insight:** The LLM **doesn't answer from its own memory** — it answers from the **chunk that was retrieved**. That's the "augmented" in Retrieval-Augmented Generation: the LLM is *augmented* with specific documents.

**Scope of the mini RAG task:** Steps **1–4** (question → embedding → search → find the closest chunk). Steps 5–6 (sending to an LLM) come later. The acceptance criterion is just: **find the correct chunk.**

**Why building 1–4 by hand matters:** This retrieval half is where most real-world bugs live (bad chunks, wrong matches). Understanding it by hand makes it clear exactly where problems come from later.

---

## 5. Hallucination

Hallucination is when an LLM **makes up information** that sounds confident but is false.

**Why it happens:** An LLM generates plausible-sounding text from patterns. If it doesn't know something, it often doesn't say "I don't know" — it invents a convincing answer.

**Example:** Asked "How many leave days do I have?", a raw LLM might guess *"20 days"* — wrong, but stated confidently.

**How RAG reduces it:** By feeding the LLM the **actual retrieved chunk**, the answer is grounded in real source text. It answers *from the document*, not from guesses. If the leave-policy chunk says 14, the LLM says 14.

---

## 6. Source Attribution

Source attribution is **citing which chunk the answer came from.**

**Why it's mandatory:**
1. **Trust** — the user can verify: "This came from the Leave Policy doc."
2. **Catching hallucination** — if the answer doesn't match its cited source, it's clear the LLM drifted.
3. **Accountability** — critical in an HR/onboarding context, where wrong answers have real consequences.

**In practice:** The answer returns not just *"14 days"* but *"14 days (source: leave_policy.txt)"*.

**Why it matters for an onboarding agent:** The system gives employees real answers. A hallucinated leave policy or a wrong VPN step is a real problem. Grounding + attribution is what makes the system **trustworthy** — not just functional.

---

## Summary

| Concept | One-line takeaway |
|---------|-------------------|
| Embedding | Text → numbers that capture meaning |
| Cosine similarity | Measures angle between vectors to score closeness |
| Chunking | Split documents so matches are precise and fit context limits |
| RAG flow | Question → embed → search → context → LLM → answer |
| Hallucination | LLMs invent confident but false answers; retrieval grounds them |
| Source attribution | Cite the source chunk for trust and verifiability |
