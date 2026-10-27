## Scene 1: Why Standard LLMs Hallucinate
[Visual: User query entering an isolated LLM node that outputs an uncertain warning callout]
Standard language models only know what was in their training data. When asked about private company docs or live events, they often guess and hallucinate.

## Scene 2: Vector Embedding and Semantic Retrieval
[Visual: User question converted into a vector embedding arrow querying a Vector Database to retrieve top relevant document chunks]
Retrieval-Augmented Generation fixes this by converting the user question into a vector embedding and searching a vector database for the most relevant document chunks.

## Scene 3: Grounded Generation with Citations
[Visual: Retrieved context chunks and user prompt flowing together into the LLM to produce a verified answer with citations]
Those verified chunks are injected directly into the model prompt, so the AI generates an accurate answer grounded in your real data with traceable citations.
