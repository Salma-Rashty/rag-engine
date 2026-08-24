# rag-engine

A minimal retrieval-augmented generation (RAG) pipeline built from scratch, without any libraries — for learning the core mechanics: embeddings, chunking, cosine similarity, and semantic search.

## What it does

Given a question and a set of documents, the script finds the chunk of text most relevant to the question. This is the **retrieval** half of a RAG system — the part that locates the right context before an LLM generates an answer.

Pipeline:

```
Question → embedding → cosine similarity search → closest chunk (with source)
```

## How it works

1. **Read** the sample documents from `data/`.
2. **Chunk** each document by paragraph (short title lines are merged into the paragraph below them).
3. **Embed** each chunk as a bag-of-words vector — a word-count fingerprint built against a shared vocabulary. No libraries, no trained models.
4. **Compare** the question's vector against every chunk's vector using hand-written cosine similarity.
5. **Return** the closest chunk along with its source file (attribution).

## Run it

```bash
python src/rag.py
```

Change the `question` variable in `src/rag.py` to test different queries.

## Project structure

```
rag-engine/
├── data/     # sample documents (synthetic, non-confidential)
├── docs/     # concept notes and test proof
│   ├── concepts/
│   └── proof/
├── src/      # the mini RAG script
└── README.md
```

## Known limitation

This uses **bag-of-words** embeddings, which match on shared *words*, not on *meaning*. Two consequences observed during testing:

- It reliably finds the correct **source document**.
- It cannot always pick the best paragraph when several contain the same keyword, because it has no sense of intent (e.g. "vacation" and "leave" are unrelated to it, despite meaning the same thing).

Solving that requires trained (neural) embeddings, which is the natural next step beyond this learning exercise. See `docs/proof/test-log.md` for the detailed test findings.