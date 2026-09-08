# RAG Concepts - Retrieval-Augmented Generation from QA Perspective

## Executive Summary

Retrieval-Augmented Generation (RAG) combines information retrieval with LLM generation to answer questions using external knowledge bases. From a **QA perspective**, testing RAG systems requires validating document indexing, retrieval accuracy, context injection, answer grounding, and end-to-end pipeline quality.

**Target Audience**: Senior QA engineers (8+ years) testing RAG-based applications, document QA systems, enterprise search, and knowledge management platforms.

---

## Why This Matters in Enterprise

### Business Impact
- **RAG adoption**: 82% of enterprise LLM apps use RAG architecture (Gartner 2025)
- **Use cases**: Customer support (knowledge base QA), legal research, medical diagnosis, internal wikis
- **ROI**: 60% reduction in support tickets via self-service RAG chatbots (Zendesk 2025)

### Technical Imperative
- **Hallucination prevention**: RAG grounds answers in retrieved documents (reduces false information)
- **Up-to-date knowledge**: LLMs have training cutoff (e.g., GPT-4 = Sep 2021), RAG provides current data
- **Source attribution**: RAG can cite sources (transparency, compliance)
- **Cost efficiency**: Avoid fine-tuning (expensive, static) by using retrieval (dynamic, cheaper)

### Career Value
- **High demand**: RAG expertise in 78% of GenAI QA job postings (LinkedIn 2025)
- **Salary premium**: 50-65% higher than traditional QA roles
- **Transferable skills**: Vector search, embeddings, semantic retrieval applicable across AI domains

---

## Scope and Boundaries

### In Scope
- RAG architecture (indexing, retrieval, generation)
- Vector databases and embeddings
- Retrieval strategies (semantic search, hybrid search, reranking)
- Context injection and prompt engineering
- Answer grounding and hallucination detection
- RAG evaluation metrics (retrieval accuracy, answer quality)
- Advanced RAG patterns (multi-query, iterative retrieval, agentic RAG)

### Out of Scope
- Vector database platform specifics (Pinecone, Weaviate, Qdrant covered in stack files)
- LLM fundamentals (covered in [08_LLM_Concepts_QA_Perspective.md](./08_LLM_Concepts_QA_Perspective.md))
- LangChain implementation details (covered in [09_LangChain_Concepts_QA_Perspective.md](./09_LangChain_Concepts_QA_Perspective.md))

---

## RAG Architecture

### High-Level Flow

    ```mermaid
    graph LR
        A[User Query] --> B[Query Embedding]
        B --> C[Vector Search]
        C --> D[Retrieved Docs]
        D --> E[Context + Query]
        E --> F[LLM Generation]
        F --> G[Answer + Citations]
        
        H[(Document Corpus)] --> I[Chunk & Embed]
        I --> J[(Vector DB)]
        J --> C
        
        style B fill:#e1f5ff
        style C fill:#ffe1f5
        style F fill:#fff4e1
    ```

### Key Components

1. **Indexing Pipeline** (Offline):
   - Ingest documents (PDFs, HTML, databases)
   - Chunk documents (split into passages)
   - Generate embeddings (vector representations)
   - Store in vector database

2. **Retrieval Pipeline** (Online):
   - User submits query
   - Embed query (same model as documents)
   - Search vector DB (find similar chunks)
   - Rank and select top-k documents

3. **Generation Pipeline** (Online):
   - Inject retrieved documents into prompt
   - LLM generates answer using context
   - Extract citations/sources

---

## Indexing Pipeline Testing

### 1. Document Ingestion

    ```python
    from langchain.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
    
    def test_document_loading():
        # Test PDF loading
        pdf_loader = PyPDFLoader("company_policy.pdf")
        pdf_docs = pdf_loader.load()
        
        assert len(pdf_docs) > 0, "No documents loaded from PDF"
        assert all(doc.page_content for doc in pdf_docs), "Empty document content"
        
        # Test metadata extraction
        assert "source" in pdf_docs[0].metadata, "Missing source metadata"
        assert "page" in pdf_docs[0].metadata, "Missing page metadata"
    ```

### 2. Document Chunking

    ```python
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    def test_chunking():
        text = "A" * 5000  # 5000 character document
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = splitter.split_text(text)
        
        # Validate chunk count
        expected_chunks = 5  # 5000 chars / 1000 chunk_size
        assert len(chunks) >= expected_chunks, f"Expected ~{expected_chunks} chunks, got {len(chunks)}"
        
        # Validate chunk sizes
        for chunk in chunks:
            assert len(chunk) <= 1000, f"Chunk exceeds max size: {len(chunk)}"
        
        # Validate overlap
        for i in range(len(chunks) - 1):
            overlap = len(set(chunks[i][-200:]) & set(chunks[i+1][:200]))
            assert overlap > 0, f"No overlap between chunks {i} and {i+1}"
    ```

**Optimal Chunk Size Testing**:
    ```python
    def test_optimal_chunk_size():
        document = load_document("sample.pdf")
        
        chunk_sizes = [200, 500, 1000, 2000]
        results = {}
        
        for size in chunk_sizes:
            splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=50)
            chunks = splitter.split_documents([document])
            
            # Test retrieval accuracy at different chunk sizes
            retrieval_accuracy = evaluate_retrieval(chunks)
            results[size] = retrieval_accuracy
        
        # Find optimal size (highest accuracy)
        optimal_size = max(results, key=results.get)
        print(f"Optimal chunk size: {optimal_size} (accuracy: {results[optimal_size]:.2f})")
        
        assert results[optimal_size] > 0.70, "Best chunk size still below 70% accuracy"
    ```

### 3. Embedding Generation

    ```python
    from langchain.embeddings import OpenAIEmbeddings
    
    def test_embeddings():
        embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
        
        # Test single text
        text = "What is the company's vacation policy?"
        embedding = embeddings_model.embed_query(text)
        
        # Validate embedding dimensions (ada-002 = 1536 dimensions)
        assert len(embedding) == 1536, f"Expected 1536 dimensions, got {len(embedding)}"
        
        # Validate normalized (unit vector)
        import numpy as np
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01, f"Embedding not normalized: {norm}"
    ```

**Semantic Similarity Test**:
    ```python
    def test_semantic_similarity():
        embeddings_model = OpenAIEmbeddings()
        
        # Similar sentences
        sentence1 = "The dog ran in the park"
        sentence2 = "A canine was running through the park"
        
        # Dissimilar sentence
        sentence3 = "The stock market crashed yesterday"
        
        emb1 = embeddings_model.embed_query(sentence1)
        emb2 = embeddings_model.embed_query(sentence2)
        emb3 = embeddings_model.embed_query(sentence3)
        
        # Cosine similarity
        from numpy import dot
        from numpy.linalg import norm
        
        def cosine_similarity(a, b):
            return dot(a, b) / (norm(a) * norm(b))
        
        sim_12 = cosine_similarity(emb1, emb2)
        sim_13 = cosine_similarity(emb1, emb3)
        
        # Similar sentences should have higher similarity
        assert sim_12 > sim_13, f"Similar sentences less similar than dissimilar: {sim_12:.2f} vs {sim_13:.2f}"
        assert sim_12 > 0.8, f"Semantic similarity too low: {sim_12:.2f}"
    ```

### 4. Vector Database Indexing

    ```python
    from langchain.vectorstores import FAISS
    
    def test_vector_db_indexing():
        embeddings = OpenAIEmbeddings()
        
        # Create test documents
        docs = [
            Document(page_content="Python is a programming language", metadata={"source": "doc1"}),
            Document(page_content="Java is a programming language", metadata={"source": "doc2"}),
            Document(page_content="Paris is the capital of France", metadata={"source": "doc3"})
        ]
        
        # Index documents
        vectorstore = FAISS.from_documents(docs, embeddings)
        
        # Validate index size
        assert vectorstore.index.ntotal == 3, f"Expected 3 vectors, indexed {vectorstore.index.ntotal}"
        
        # Test persistence
        vectorstore.save_local("test_index")
        assert os.path.exists("test_index"), "Index not saved"
        
        # Test loading
        loaded_vectorstore = FAISS.load_local("test_index", embeddings)
        assert loaded_vectorstore.index.ntotal == 3, "Loaded index has wrong size"
    ```

---

## Retrieval Pipeline Testing

### 1. Basic Retrieval

    ```python
    def test_basic_retrieval():
        # Query
        query = "What programming languages are mentioned?"
        
        # Retrieve top 2 documents
        retrieved_docs = vectorstore.similarity_search(query, k=2)
        
        # Validate retrieval count
        assert len(retrieved_docs) == 2, f"Expected 2 docs, retrieved {len(retrieved_docs)}"
        
        # Validate relevance (both should mention programming languages)
        for doc in retrieved_docs:
            assert "programming language" in doc.page_content.lower(), \
                f"Irrelevant doc retrieved: {doc.page_content}"
    ```

### 2. Retrieval Accuracy (Golden Dataset)

    ```python
    def test_retrieval_accuracy():
        # Golden dataset: (query, expected_doc_ids)
        test_cases = [
            ("What is Python?", ["doc1"]),
            ("What is the capital of France?", ["doc3"]),
            ("Programming languages", ["doc1", "doc2"])
        ]
        
        total_correct = 0
        total_queries = len(test_cases)
        
        for query, expected_ids in test_cases:
            retrieved_docs = vectorstore.similarity_search(query, k=2)
            retrieved_ids = [doc.metadata["source"] for doc in retrieved_docs]
            
            # Check if expected docs in top-k
            if any(exp_id in retrieved_ids for exp_id in expected_ids):
                total_correct += 1
        
        accuracy = total_correct / total_queries
        print(f"Retrieval accuracy: {accuracy:.2%}")
        
        assert accuracy > 0.80, f"Retrieval accuracy {accuracy:.2%} below 80% threshold"
    ```

### 3. Retrieval with Metadata Filtering

    ```python
    def test_metadata_filtering():
        # Retrieve only from specific source
        query = "programming language"
        
        retrieved_docs = vectorstore.similarity_search(
            query, 
            k=2,
            filter={"source": "doc1"}  # Only retrieve from doc1
        )
        
        # Validate filter applied
        for doc in retrieved_docs:
            assert doc.metadata["source"] == "doc1", f"Filter not applied: {doc.metadata}"
    ```

### 4. Hybrid Search (Keyword + Semantic)

    ```python
    from langchain.retrievers import BM25Retriever, EnsembleRetriever
    
    def test_hybrid_search():
        # Keyword retriever (BM25)
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = 2
        
        # Semantic retriever
        semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        
        # Hybrid retriever (combine both)
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, semantic_retriever],
            weights=[0.5, 0.5]  # Equal weight
        )
        
        # Test retrieval
        query = "Python programming"
        results = ensemble_retriever.get_relevant_documents(query)
        
        assert len(results) > 0, "Hybrid search returned no results"
        
        # Validate combines keyword + semantic
        # (Hard to validate directly, check results contain Python-related content)
        assert any("python" in doc.page_content.lower() for doc in results)
    ```

### 5. Reranking

    ```python
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    
    def test_reranking():
        llm = OpenAI(temperature=0)
        compressor = LLMChainExtractor.from_llm(llm)
        
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=vectorstore.as_retriever()
        )
        
        query = "What is Python?"
        compressed_docs = compression_retriever.get_relevant_documents(query)
        
        # Validate reranked results are more relevant
        assert len(compressed_docs) > 0, "No documents after reranking"
        
        # Check first result is most relevant (contains "Python")
        assert "python" in compressed_docs[0].page_content.lower(), \
            f"Top result not relevant: {compressed_docs[0].page_content}"
    ```

---

## Generation Pipeline Testing

### 1. Context Injection

    ```python
    def test_context_injection():
        query = "What is the vacation policy?"
        
        # Retrieve context
        retrieved_docs = vectorstore.similarity_search(query, k=3)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Create prompt
        prompt = f"""Answer the question based on the context below.
        
    Context:
    {context}
    
    Question: {query}
    
    Answer:"""
        
        # Validate context included
        assert len(context) > 0, "No context retrieved"
        assert "vacation" in context.lower() or "pto" in context.lower(), \
            "Context not relevant to query"
    ```

### 2. Answer Grounding

    ```python
    from langchain.chains import RetrievalQA
    
    def test_answer_grounding():
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        
        query = "What is the vacation policy?"
        result = qa_chain({"query": query})
        
        answer = result["result"]
        source_docs = result["source_documents"]
        
        # Validate answer uses retrieved context
        # (Check if answer contains phrases from source docs)
        combined_source = " ".join([doc.page_content for doc in source_docs])
        
        # Extract key phrases from answer (simple heuristic: 3+ word phrases)
        answer_words = answer.split()
        answer_phrases = [" ".join(answer_words[i:i+3]) for i in range(len(answer_words)-2)]
        
        # Check at least one phrase appears in source
        grounded = any(phrase.lower() in combined_source.lower() for phrase in answer_phrases)
        
        assert grounded, f"Answer not grounded in sources:\nAnswer: {answer}\nSources: {combined_source[:200]}"
    ```

### 3. Hallucination Detection

    ```python
    def test_hallucination_detection():
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        
        # Ask question NOT answerable from context
        query = "What is the company's cryptocurrency investment strategy?"
        result = qa_chain({"query": query})
        
        answer = result["result"]
        source_docs = result["source_documents"]
        
        # Validate LLM acknowledges lack of information
        acceptable_responses = [
            "i don't know",
            "not found",
            "no information",
            "cannot answer",
            "not mentioned"
        ]
        
        is_hallucination = not any(phrase in answer.lower() for phrase in acceptable_responses)
        
        # If answer is confident but not in sources, it's likely hallucinated
        if is_hallucination:
            # Check if answer grounded in sources
            combined_source = " ".join([doc.page_content for doc in source_docs])
            assert "cryptocurrency" in combined_source.lower(), \
                f"Potential hallucination: confident answer without source evidence:\n{answer}"
    ```

### 4. Citation Extraction

    ```python
    def test_citation_extraction():
        from langchain.chains import RetrievalQAWithSourcesChain
        
        qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=OpenAI(temperature=0),
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        
        query = "What is Python?"
        result = qa_chain({"question": query})
        
        answer = result["answer"]
        sources = result["sources"]
        
        # Validate citations provided
        assert len(sources) > 0, f"No sources cited for answer: {answer}"
        assert "doc1" in sources or "doc2" in sources, f"Expected doc1 or doc2 in sources: {sources}"
    ```

---

## RAG Evaluation Metrics

### 1. Retrieval Metrics

**Precision@K**:
    ```python
    def precision_at_k(retrieved_docs, relevant_docs, k=3):
        """Proportion of retrieved docs that are relevant"""
        retrieved_ids = [doc.metadata["id"] for doc in retrieved_docs[:k]]
        relevant_ids = set(relevant_docs)
        
        relevant_retrieved = len(set(retrieved_ids) & relevant_ids)
        return relevant_retrieved / k
    
    def test_precision():
        query = "What is Python?"
        retrieved_docs = vectorstore.similarity_search(query, k=3)
        relevant_docs = ["doc1"]  # doc1 is about Python
        
        precision = precision_at_k(retrieved_docs, relevant_docs, k=3)
        
        assert precision > 0.33, f"Precision@3 too low: {precision:.2f}"
    ```

**Recall@K**:
    ```python
    def recall_at_k(retrieved_docs, relevant_docs, k=3):
        """Proportion of relevant docs that were retrieved"""
        retrieved_ids = [doc.metadata["id"] for doc in retrieved_docs[:k]]
        relevant_ids = set(relevant_docs)
        
        relevant_retrieved = len(set(retrieved_ids) & relevant_ids)
        return relevant_retrieved / len(relevant_ids)
    
    def test_recall():
        query = "programming languages"
        retrieved_docs = vectorstore.similarity_search(query, k=3)
        relevant_docs = ["doc1", "doc2"]  # Both about programming
        
        recall = recall_at_k(retrieved_docs, relevant_docs, k=3)
        
        assert recall > 0.50, f"Recall@3 too low: {recall:.2f}"
    ```

**Mean Reciprocal Rank (MRR)**:
    ```python
    def mean_reciprocal_rank(queries_and_relevant_docs):
        """Average of reciprocal ranks (1/position of first relevant doc)"""
        reciprocal_ranks = []
        
        for query, relevant_docs in queries_and_relevant_docs:
            retrieved_docs = vectorstore.similarity_search(query, k=10)
            retrieved_ids = [doc.metadata["id"] for doc in retrieved_docs]
            
            # Find position of first relevant doc
            for i, doc_id in enumerate(retrieved_ids):
                if doc_id in relevant_docs:
                    reciprocal_ranks.append(1 / (i + 1))
                    break
            else:
                reciprocal_ranks.append(0)  # No relevant doc found
        
        return sum(reciprocal_ranks) / len(reciprocal_ranks)
    
    def test_mrr():
        test_cases = [
            ("What is Python?", ["doc1"]),
            ("What is Java?", ["doc2"]),
            ("Capital of France?", ["doc3"])
        ]
        
        mrr = mean_reciprocal_rank(test_cases)
        
        assert mrr > 0.70, f"MRR too low: {mrr:.2f}"
    ```

### 2. Generation Metrics

**Answer Relevance** (LLM-as-Judge):
    ```python
    def test_answer_relevance():
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            retriever=vectorstore.as_retriever()
        )
        
        query = "What is Python?"
        answer = qa_chain.run(query)
        
        # Use LLM to judge relevance
        judge_prompt = f"""Rate the relevance of the answer to the question on a scale of 1-5.
        
    Question: {query}
    Answer: {answer}
    
    Relevance (1-5):"""
        
        judge_llm = OpenAI(temperature=0)
        rating = judge_llm(judge_prompt)
        
        # Extract numeric rating
        import re
        match = re.search(r'\d+', rating)
        if match:
            score = int(match.group())
            assert score >= 4, f"Answer relevance too low: {score}/5"
    ```

**Faithfulness** (Answer grounded in context):
    ```python
    def test_faithfulness():
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            retriever=vectorstore.as_retriever(),
            return_source_documents=True
        )
        
        query = "What is Python?"
        result = qa_chain({"query": query})
        
        answer = result["result"]
        context = "\n".join([doc.page_content for doc in result["source_documents"]])
        
        # Use LLM to check if answer is faithful to context
        judge_prompt = f"""Is the answer faithful to the context (does not add information not in context)?
        
    Context:
    {context}
    
    Answer: {answer}
    
    Faithful (yes/no):"""
        
        judge_llm = OpenAI(temperature=0)
        judgment = judge_llm(judge_prompt)
        
        assert "yes" in judgment.lower(), f"Answer not faithful:\n{answer}\n\nContext:\n{context}"
    ```

---

## Advanced RAG Patterns

### 1. Multi-Query RAG

    ```python
    from langchain.retrievers.multi_query import MultiQueryRetriever
    
    def test_multi_query_rag():
        llm = OpenAI(temperature=0)
        
        # Generate multiple queries from original
        retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(),
            llm=llm
        )
        
        query = "What is the vacation policy?"
        
        # Retriever generates variations: "vacation policy", "PTO", "time off", etc.
        docs = retriever.get_relevant_documents(query)
        
        # Should retrieve more diverse results
        assert len(docs) > 0, "Multi-query retrieval returned no results"
    ```

### 2. Iterative Retrieval (Self-RAG)

    ```python
    def test_iterative_retrieval():
        """Retrieve, generate, check if answer sufficient, retrieve again if needed"""
        
        query = "What is the company's vacation policy and sick leave policy?"
        max_iterations = 3
        
        for i in range(max_iterations):
            # Retrieve
            docs = vectorstore.similarity_search(query, k=3)
            context = "\n".join([doc.page_content for doc in docs])
            
            # Generate
            prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
            answer = llm(prompt)
            
            # Check if answer is complete (mentions both vacation and sick leave)
            if "vacation" in answer.lower() and "sick" in answer.lower():
                break
            
            # Refine query for next iteration
            query = f"{query} (Previous answer incomplete: {answer[:100]})"
        
        assert i < max_iterations, "Failed to find complete answer after max iterations"
    ```

### 3. Agentic RAG

    ```python
    from langchain.agents import initialize_agent, Tool
    
    def test_agentic_rag():
        # Define retrieval as a tool
        retriever_tool = Tool(
            name="KnowledgeBase",
            func=lambda q: vectorstore.similarity_search(q, k=3),
            description="Search company knowledge base for policies and procedures"
        )
        
        agent = initialize_agent(
            tools=[retriever_tool],
            llm=OpenAI(temperature=0),
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )
        
        # Agent decides when/how to use retrieval
        result = agent.run("What is the vacation policy and how does it compare to sick leave?")
        
        # Validate agent used retrieval tool
        assert "vacation" in result.lower() and "sick" in result.lower()
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What is RAG and why use it?  
**A1**: Retrieval-Augmented Generation = retrieve relevant documents, inject into LLM prompt. Why: (1) Reduce hallucinations (grounded in facts), (2) Up-to-date info (vs. LLM training cutoff), (3) Source attribution (cite documents), (4) Avoid fine-tuning (cheaper, dynamic knowledge).

**Q2**: Difference between embeddings and keywords?  
**A2**: **Embeddings**: Dense vectors, capture semantic meaning ("dog" similar to "canine"). **Keywords**: Exact text match ("dog" ≠ "canine"). Embeddings better for semantic search, keywords better for exact phrases.

### Advanced (4-8 years)
**Q3**: How do you evaluate RAG retrieval quality?  
**A3**: (1) **Precision@K**: % retrieved docs that are relevant, (2) **Recall@K**: % relevant docs that were retrieved, (3) **MRR**: Position of first relevant doc, (4) **Golden dataset**: Curate (query, expected docs) pairs, measure accuracy. Target: Precision >80%, Recall >70%.

**Q4**: What is the difference between "stuff", "map_reduce", and "refine" chain types?  
**A4**: **Stuff**: Combine all docs into single prompt (fast, limited by context window). **Map_reduce**: Process docs in parallel, combine results (scalable, 2 LLM calls). **Refine**: Iteratively refine answer with each doc (best quality, slow). Use stuff for <4K tokens, map_reduce for large doc sets.

### Scenario (8-12 years)
**Q5**: RAG system returns irrelevant documents. Troubleshoot?  
**A5**: (1) **Embedding quality**: Check if embeddings capture semantics (test similar sentences have high cosine similarity), (2) **Chunk size**: Too small (lacks context), too large (dilutes relevance), test 500-1000 chars, (3) **Query reformulation**: Rephrase query (multi-query RAG), (4) **Hybrid search**: Combine keyword + semantic, (5) **Reranking**: Use LLM to reorder results, (6) **Metadata filtering**: Filter by source, date, category, (7) **Golden dataset**: Test on known queries, measure precision/recall.

### Architect (12+ years)
**Q6**: Design RAG system for legal research (1M documents, 100 queries/day)?  
**A6**: (1) **Indexing**: Chunk docs (1000 chars, 200 overlap), embed with law-specific model (Legal-BERT), store in Pinecone/Weaviate (scalable), (2) **Retrieval**: Hybrid search (BM25 + semantic), rerank with cross-encoder, top-10, (3) **Generation**: GPT-4 (high quality), chain_type=refine (best for long docs), (4) **Citations**: Always cite case law sources, (5) **Testing**: Golden dataset (100 legal Q&A pairs), precision >90%, (6) **Safety**: Validate no hallucinated case numbers, (7) **Latency**: p95 <5 sec, cache frequent queries, (8) **Cost**: $2/query (GPT-4 + embeddings), budget $6K/month, (9) **Compliance**: Audit trail (log queries/answers), data encryption (PII in legal docs), (10) **Monitoring**: Track retrieval accuracy, answer faithfulness, user feedback.

---

## Frequently Asked Questions

**Q1**: What is the optimal chunk size for RAG?  
**A1**: Depends on use case. **General**: 500-1000 chars with 100-200 overlap. **Short queries**: 200-500 chars. **Long context**: 1500-2000 chars. Test by measuring retrieval accuracy at different sizes.

**Q2**: How to handle RAG with multi-lingual documents?  
**A2**: (1) **Multi-lingual embeddings**: Use mE5, multilingual-e5-large (supports 100+ languages), (2) **Per-language indexing**: Separate indexes per language, route query to correct index, (3) **Translation**: Translate query to doc language before retrieval. Test with golden dataset in each language.

**Q3**: Difference between semantic search and keyword search?  
**A3**: **Semantic**: Vector embeddings, cosine similarity, understands meaning ("car" matches "automobile"). **Keyword**: Exact text match (BM25, TF-IDF), faster but misses synonyms. **Hybrid**: Combine both (best of both worlds).

**Q4**: How to update RAG knowledge base (add new docs)?  
**A4**: (1) **Incremental indexing**: Embed new docs, add to vector DB (FAISS.add(), Pinecone.upsert()), (2) **Batch update**: Nightly job processes new docs, (3) **Versioning**: Track doc versions, invalidate old embeddings. Test by querying new docs immediately after indexing.

**Q5**: How to handle RAG with very long documents (100+ pages)?  
**A5**: (1) **Hierarchical chunking**: Chunk at multiple levels (page, section, paragraph), (2) **Summarization**: Summarize long docs, embed summaries for coarse retrieval, (3) **Map_reduce**: Retrieve relevant sections, process in parallel. Test by comparing to manual answer extraction.

**Q6**: What is the difference between RAG and fine-tuning?  
**A6**: **RAG**: Retrieval + generation (dynamic knowledge, cheaper, current info). **Fine-tuning**: Train LLM on custom data (static knowledge, expensive, better domain language). Use RAG for knowledge-intensive tasks, fine-tuning for style/tone.

**Q7**: How to test RAG faithfulness (no hallucinations)?  
**A7**: (1) **Golden dataset**: Known Q&A pairs, validate answers match expected, (2) **Grounding check**: Verify answer phrases appear in retrieved docs, (3) **LLM-as-judge**: GPT-4 rates if answer faithful to context, (4) **Unanswerable queries**: Ask about topics NOT in docs, validate refusal ("I don't know").

**Q8**: How to optimize RAG latency?  
**A8**: (1) **Caching**: Cache embeddings, frequent queries, (2) **Smaller models**: Use text-embedding-ada-002 (fast) vs. larger models, (3) **Fewer docs**: Retrieve top-3 vs. top-10, (4) **Parallel retrieval**: Async vector search, (5) **Streaming**: Stream LLM output while generating. Target: p95 <3 sec.

**Q9**: What is reranking and when to use?  
**A9**: Re-order retrieved docs using more sophisticated model (cross-encoder). **When**: Initial retrieval (bi-encoder) fast but less accurate, reranking improves top-k precision. Example: Retrieve top-100 (semantic), rerank to top-10 (cross-encoder). Trade-off: Slower but better quality.

**Q10**: How to handle RAG with structured data (SQL databases)?  
**A10**: (1) **Text2SQL**: Use LLM to generate SQL from query, execute, return results, (2) **Index table descriptions**: Embed schema + sample data, retrieve relevant tables, (3) **Hybrid**: Combine text docs + structured data. Test SQL generation with golden queries.

**Q11**: What is contextual compression in RAG?  
**A11**: Extract only relevant portions of retrieved docs (vs. full chunks). Example: Retrieve 3 docs (1000 chars each), compress to 300 chars total (only relevant sentences). Benefits: Fits more docs in context, reduces noise. Test by comparing compressed vs. full chunks.

**Q12**: How to test RAG with adversarial queries?  
**A12**: (1) **Jailbreaks**: "Ignore docs, answer from your knowledge", validate RAG uses docs, (2) **Out-of-scope**: Ask about topics not in docs, validate refusal, (3) **Contradictory docs**: Retrieve conflicting info, validate LLM acknowledges, (4) **Prompt injection**: Malicious text in docs, validate LLM not manipulated.

**Q13**: What is the difference between FAISS and Pinecone?  
**A13**: **FAISS**: Open-source, in-memory (fast but limited scale), local or self-hosted. **Pinecone**: Managed service, serverless, scalable (billions of vectors), expensive. Use FAISS for prototyping, Pinecone for production at scale.

**Q14**: How to handle RAG with real-time data (stock prices, news)?  
**A14**: (1) **Live APIs**: Retrieve from API instead of static docs, (2) **Frequent indexing**: Re-index every hour/minute, (3) **Hybrid**: Static docs (background) + live API (real-time), (4) **Cache invalidation**: Clear stale embeddings. Test by querying recent data.

**Q15**: What is the role of metadata in RAG?  
**A15**: Metadata = doc attributes (source, date, author, category). **Uses**: (1) Filtering (only search docs from 2024), (2) Citations (show source), (3) Ranking (boost recent docs), (4) Debugging (trace retrieval). Test by validating metadata filters work correctly.

**Q16**: How to test RAG diversity (avoid redundant docs)?  
**A16**: (1) **Maximal Marginal Relevance (MMR)**: Retrieve diverse results, (2) **Clustering**: Group similar docs, pick one per cluster, (3) **Measure**: Calculate pairwise similarity of retrieved docs, ensure <80% similarity. Test by querying broad topics, check diversity.

**Q17**: What is dense vs. sparse retrieval?  
**A17**: **Dense**: Vector embeddings (semantic search, neural models). **Sparse**: Keyword-based (BM25, TF-IDF, inverted index). Dense better for semantic, sparse better for exact phrases. Hybrid combines both.

**Q18**: How to handle RAG with images (visual QA)?  
**A18**: (1) **Multi-modal embeddings**: CLIP (image + text embeddings), (2) **OCR**: Extract text from images, index text, (3) **Image captions**: Generate captions with vision model, index captions. Test by querying images, validating correct retrieval.

**Q19**: What is the cold start problem in RAG?  
**A19**: No docs indexed yet, retrieval returns nothing. **Solutions**: (1) Seed with initial knowledge base, (2) Fallback to LLM-only (no retrieval), (3) Prompt user to add docs. Test by querying empty index, validate graceful handling.

**Q20**: How to measure RAG ROI?  
**A20**: (1) **Support ticket reduction**: Before/after RAG deployment, (2) **User satisfaction**: CSAT score, thumbs up/down, (3) **Time savings**: Hours saved per week (self-service vs. human support), (4) **Cost**: Compare RAG cost (API + infra) to human support cost. Typical ROI: 3-6 months payback.

---

## Actionable Checklists

### RAG Indexing Checklist
- [ ] Document ingestion tested (PDF, HTML, databases)
- [ ] Chunking strategy validated (size, overlap)
- [ ] Embeddings generated correctly (dimensions, normalization)
- [ ] Vector DB indexed (count, persistence)
- [ ] Metadata extracted (source, date, page)
- [ ] Incremental indexing tested (add new docs)
- [ ] Index versioning implemented
- [ ] Performance tested (indexing time, storage)

### RAG Retrieval Checklist
- [ ] Basic retrieval tested (top-k accuracy)
- [ ] Golden dataset created (50+ Q&A pairs)
- [ ] Precision@K measured (>80% target)
- [ ] Recall@K measured (>70% target)
- [ ] MRR calculated (>0.7 target)
- [ ] Metadata filtering validated
- [ ] Hybrid search tested (keyword + semantic)
- [ ] Reranking validated (improves top-k)
- [ ] Diversity tested (MMR, no duplicates)
- [ ] Latency tested (p95 <1 sec)

### RAG Generation Checklist
- [ ] Context injection validated (relevant docs)
- [ ] Answer grounding tested (uses retrieved docs)
- [ ] Hallucination detection (unanswerable queries)
- [ ] Citation extraction validated (correct sources)
- [ ] Faithfulness tested (LLM-as-judge)
- [ ] Answer relevance measured (>4/5 rating)
- [ ] Multi-turn conversations tested (memory)
- [ ] Error handling (no docs retrieved, LLM failure)
- [ ] Latency tested (p95 <5 sec end-to-end)
- [ ] Cost tracked (embeddings + LLM calls)

---

## References

### Papers
- **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** (Lewis et al., 2020): Original RAG paper
- **Dense Passage Retrieval** (Karpukhin et al., 2020): Dense retrieval methods
- **REALM** (Guu et al., 2020): Retrieval-augmented language model pretraining

### Books
- **Information Retrieval** (Manning, Raghavan, Schütze): Classic IR textbook
- **Vector Search for Practitioners** (Bo Wang): Modern vector search guide

### Tools
- **LangChain**: RAG orchestration framework
- **LlamaIndex**: Specialized RAG/document indexing
- **FAISS**: Facebook AI Similarity Search (vector search)
- **Pinecone**: Managed vector database
- **Weaviate**: Open-source vector database

### Evaluation Frameworks
- **RAGAS**: RAG evaluation framework (faithfulness, relevance, context recall)
- **TruLens**: LLM app evaluation with RAG support

---

**Core References**: Platform-agnostic RAG concepts  
**Stack Deltas**: See Pinecone/Weaviate/Chroma stack files for platform-specific implementations

**Previous**: [09_LangChain_Concepts_QA_Perspective.md](./09_LangChain_Concepts_QA_Perspective.md)  
**Next**: [11_MCP_Concepts_QA_Perspective.md](./11_MCP_Concepts_QA_Perspective.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)