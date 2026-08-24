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

<!-- More tests added below as changes are made. -->
