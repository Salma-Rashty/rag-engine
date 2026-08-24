import os
import re
import math

# Folder where the 3 sample documents live
DATA_FOLDER = "data"

def read_documents(folder):
    """Read every .txt file in the folder into a dictionary: {filename: text}."""
    documents = {}                          # will hold filename -> content
    for filename in os.listdir(folder):     # loop over files in data/
        if filename.endswith(".txt"):       # only take text files
            path = os.path.join(folder, filename)   # build full path, e.g. data/leave_policy.txt
            with open(path, "r", encoding="utf-8") as f:  # open file safely
                documents[filename] = f.read()          # store its text under its filename
    return documents

# Test it
docs = read_documents(DATA_FOLDER)
for name in docs:
    print(name)          # print each filename to confirm all 3 loaded


def chunk_text(text):
    """Split text into chunks by paragraph, merging short title-like lines
    into the paragraph that follows them."""
    raw_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]

    merged = []
    i = 0
    while i < len(raw_chunks):
        current = raw_chunks[i]

        # If a chunk is very short (likely a title) and there's a next chunk,
        # merge it INTO the next one.
        if len(current.split()) < 5 and i + 1 < len(raw_chunks):
            merged.append(current + " " + raw_chunks[i + 1])
            i += 2                     # skip the next one, we already used it
        else:
            merged.append(current)
            i += 1

    return merged


def chunk_documents(documents):
    """Turn {filename: text} into a list of chunks, each remembering its source file."""
    all_chunks = []                         # will hold every chunk from every file
    for filename, text in documents.items():
        for chunk in chunk_text(text):
            all_chunks.append({             # store chunk + its source together
                "source": filename,         # needed later for attribution
                "text": chunk
            })
    return all_chunks

# Test it
chunks = chunk_documents(docs)
print(f"\nTotal chunks: {len(chunks)}\n")
for c in chunks:
    print(f"[{c['source']}] {c['text'][:50]}...")   # show source + first 50 chars


def tokenize(text):
    """Break text into lowercase words, stripping punctuation."""
    # \w+ matches sequences of letters/numbers; lowercase so "Leave" == "leave"
    return re.findall(r"\w+", text.lower())


def build_vocabulary(chunks):
    """Collect every unique word across all chunks into a sorted list."""
    vocab = set()                           # a set auto-removes duplicates
    for chunk in chunks:
        for word in tokenize(chunk["text"]):
            vocab.add(word)
    return sorted(vocab)                     # sort so word positions are fixed


def text_to_vector(text, vocabulary):
    """Turn text into a word-count vector aligned to the vocabulary."""
    words = tokenize(text)
    # For each vocab word (in order), count how many times it appears in this text
    return [words.count(vocab_word) for vocab_word in vocabulary]

# Test it
vocabulary = build_vocabulary(chunks)
print(f"\nVocabulary size: {len(vocabulary)} words\n")

# Turn every chunk into a vector, keeping its source + text
for chunk in chunks:
    chunk["vector"] = text_to_vector(chunk["text"], vocabulary)

# Show one example
print("Example chunk:", chunks[0]["text"][:40])
print("Its vector (first 15 numbers):", chunks[0]["vector"][:15])

# Show which words actually have counts in this chunk
example = chunks[0]
for word, count in zip(vocabulary, example["vector"]):
    if count > 0:                    # only show words that appear
        print(f"{word}: {count}")



def dot_product(vec_a, vec_b):
    """Multiply matching positions and sum them up."""
    # zip pairs up position 0 with 0, 1 with 1, etc.
    return sum(a * b for a, b in zip(vec_a, vec_b))


def magnitude(vec):
    """Length of a vector: square root of the sum of its squared values."""
    return math.sqrt(sum(value * value for value in vec))


def cosine_similarity(vec_a, vec_b):
    """Cosine similarity = dot product divided by the product of magnitudes."""
    dot = dot_product(vec_a, vec_b)
    mag_a = magnitude(vec_a)
    mag_b = magnitude(vec_b)

    # Guard against division by zero (empty vector)
    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)

# Test it with two simple vectors
v1 = [1, 1, 0]
v2 = [1, 1, 0]      # identical → should score 1.0
v3 = [0, 0, 1]      # unrelated → should score 0.0

print("\nIdentical vectors:", cosine_similarity(v1, v2))   # expect 1.0
print("Unrelated vectors:", cosine_similarity(v1, v3),"\n")   # expect 0.0

def find_closest_chunk(question, chunks, vocabulary):
    """Find the chunk most similar to the question using cosine similarity."""
    # Turn the question into a vector using the SAME vocabulary as the chunks
    question_vector = text_to_vector(question, vocabulary)

    best_chunk = None
    best_score = -1                          # start lower than any possible score

    for chunk in chunks:
        score = cosine_similarity(question_vector, chunk["vector"])
        if score > best_score:               # keep the highest-scoring chunk
            best_score = score
            best_chunk = chunk

    return best_chunk, best_score

# Test it with a question
# Only uncomment one question at a time to see the results clearly

# question = "How many annual leave days do I have?"
# question = "How do I set up the VPN?"
question = "What time does the shuttle leave?"

best_chunk, score = find_closest_chunk(question, chunks, vocabulary)

print(f"Question: {question}\n")
print(f"Best match (score: {score:.3f})")
print(f"Source: {best_chunk['source']}")     # attribution
print(f"Chunk text:\n{best_chunk['text']}")