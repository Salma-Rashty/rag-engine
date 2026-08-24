# Mini RAG — Test Log

Testing the library-free mini RAG: questions, results, observations, and changes. Screenshots referenced inline as proof.

---

## Test 1 — Leave question

**Setup:** paragraph chunking · bag-of-words vectors · hand-built cosine

**Question:** "How many annual leave days do I have?"

**Result:**
- Source: `leave_policy.txt` ✅ correct file
- Score: 0.577
- Chunk returned: `"Annual Leave Policy"` (title only)

*(See screenshot/image1.png)*

**Observation:** Right file, but returned the **title**, not the paragraph with the answer ("14 days").

**Why:** The title is its own tiny chunk. Short chunks let a few matching words dominate, so they outscore the longer answer paragraph.

---

## Test 2 — VPN question

**Question:** "How do I set up the VPN?"

**Result:**
- Source: `it_setup.txt` ✅ correct file
- Score: 0.516
- Chunk returned: 2nd paragraph (email setup *after* VPN)

*(See screenshot/image2.png)*

**Observation:** Right file, but matched the **wrong paragraph** — the one about steps *after* the VPN, not the one explaining how to download it.

**Why:** Both paragraphs mention "VPN". The 2nd says "installing the VPN", giving slightly more word overlap with the question. Bag-of-words matches shared words, not meaning.

---

## Test 3 — Shuttle question

**Question:** "What time does the shuttle leave?"

**Result:**
- Source: `meals_shuttle.txt` ✅ correct file
- Score: 0.497
- Chunk returned: correct paragraph (shuttle leaves at 18.00) ✅

*(See screenshot/image3.png)*

**Observation:** Clean hit — right file and right paragraph. "Shuttle" appears several times in the chunk, so it scored clearly highest.

---

## Summary so far

| Question | Correct file | Correct paragraph |
|----------|:---:|:---:|
| Leave days | ✅ | ❌ (got title) |
| VPN setup | ✅ | ⚠️ (2nd para) |
| Shuttle | ✅ | ✅ |

All three pass the acceptance criterion (correct file). Two show the bag-of-words limitation: it matches shared **words**, not **meaning**, and short chunks can score misleadingly high.

**Next:** try a chunking fix (merge titles into paragraphs / filter very short chunks) and compare results.

---


## Chunking fix — merge short titles into the next paragraph

**Change made:** Updated `chunk_text` so any very short chunk (< 5 words, likely a title) is merged into the paragraph that follows it. This targets the Test 1 problem where the title "Annual Leave Policy" was its own tiny chunk.

---

## Test 4 — Leave question (after fix)

**Question:** "How many annual leave days do I have?"

**Result:**
- Source: `leave_policy.txt` ✅
- Score: 0.506
- Chunk returned: title **+ paragraph with "14 days"** ✅

*(See screenshot/image4.png)*

**Observation:** Fixed. The title merged into its paragraph, so the returned chunk now contains the actual answer.

**Key insight:** The score dropped (0.577 → 0.506) even though the answer is now correct. The longer merged chunk dilutes the matching words, lowering the score. **A higher score does not mean a better answer** — the old high score was misleadingly high.

---

## Test 5 — VPN question (after fix)

**Question:** "How do I set up the VPN?"

**Result:**
- Source: `it_setup.txt` ✅
- Score: 0.516 (unchanged)
- Chunk returned: 2nd paragraph (still) ⚠️

*(See screenshot/image5.png)*

**Observation:** Unchanged, and correctly so — neither VPN paragraph is a short title, so the merge doesn't apply here. This is a **different problem**: both paragraphs contain "VPN", and the 2nd has slightly more word overlap ("installing the VPN") with the question. Bag-of-words matches shared words, not meaning, so it can't tell the 1st paragraph is the better answer. This limitation needs real (neural) embeddings, not a chunking change.

---

## Test 6 — Shuttle question (after fix)

**Question:** "What time does the shuttle leave?"

**Result:**
- Source: `meals_shuttle.txt` ✅
- Score: 0.497
- Chunk returned: correct paragraph (18.00) ✅

*(See screenshot/image6.png)*

**Observation:** Unchanged and still correct — the fix didn't affect or break it.

---

## Summary after fix

| Question | File | Paragraph | Status |
|----------|:---:|:---:|--------|
| Leave | ✅ | ✅ | Fixed by chunking change |
| VPN | ✅ | ⚠️ | Needs real embeddings (word vs. meaning) |
| Shuttle | ✅ | ✅ | Was already correct |

**Two distinct findings:**
1. **Short-chunk / title problem** → solved with better chunking.
2. **Word-matching vs. meaning problem** → not solvable by chunking; this is the core limit of bag-of-words embeddings and why the real project will use trained embedding models.

