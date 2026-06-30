# GridPolicy-RAG

**GridPolicy-RAG** is a citation-grounded Retrieval-Augmented Generation system for Australian energy infrastructure and grid regulation documents.

The project focuses on public AEMO documents, including Integrated System Plan reports, Electricity Statement of Opportunities reports, operational procedures, power system security guidelines, and related workbooks. Its goal is to answer technical questions about Australian energy markets, grid planning, system reliability, dispatch, capacity, and regulatory requirements while reducing hallucinations through evidence-based retrieval and source citations.

## Project Goal

Large energy-market and grid-regulation PDFs often contain dense technical language, numerical values, tables, units, abbreviations, and policy conditions. General-purpose LLMs may hallucinate or misrepresent these details.

GridPolicy-RAG aims to build a domain-specific RAG pipeline that:

* Parses AEMO PDF documents and related data files.
* Extracts text, layout information, tables, and metadata.
* Builds searchable text and table chunks.
* Uses hybrid retrieval to find relevant evidence.
* Generates answers only from retrieved document passages.
* Provides citations with document title, section, page number, and table reference.
* Refuses to answer when the retrieved evidence is insufficient.

## System Architecture

The system follows the pipeline:

```text
AEMO PDFs
→ PDF parsing
→ region detection
→ text and table extraction
→ cleaning and normalization
→ section-aware chunking
→ embedding generation
→ vector database indexing
→ hybrid retrieval
→ reranking
→ prompt construction
→ LLM answer generation
→ citation-grounded response
```

## Main Features

* PDF ingestion for AEMO reports and operational documents.
* Document registry generation for tracking raw files and metadata.
* Layout-aware parsing with page number, coordinates, section title, and document ID.
* Table and chart region detection for complex technical pages.
* Text chunks stored with citation metadata.
* Hybrid retrieval using BM25 and vector search.
* Optional reranking for improving evidence precision.
* Citation-constrained generation to reduce hallucination.
* Evaluation on factual, numerical, table-based, multi-document, and unanswerable questions.
* FastAPI backend and Streamlit demo interface.

## Technology Stack

* **Language:** Python
* **PDF Parsing:** PyMuPDF, pdfplumber, Unstructured or Docling
* **Table Extraction:** pdfplumber, Camelot, layout-aware region detection
* **Embeddings:** BGE, E5, GTE, or sentence-transformers
* **Vector Database:** FAISS, Chroma, or Qdrant
* **Keyword Retrieval:** BM25
* **Reranking:** BGE reranker or Cohere Rerank
* **LLM API:** GPT, Claude, Gemini, or DeepSeek
* **Backend:** FastAPI
* **Demo UI:** Streamlit
* **Deployment:** Docker

## Example Questions

```text
What reliability risks does the 2025 ESOO identify for the NEM?

What projected capacity shortfall or surplus is reported for 2030?

What does AEMO say about system security requirements under high renewable penetration?

Which documents mention Renewable Energy Zones, and how are they described?

What operational conditions are required for maintaining power system security?

Does the document provide enough evidence to answer whether a specific new project is approved?
```

## Evaluation Plan

The project includes a small benchmark dataset covering:

* Factual lookup questions
* Numerical value questions
* Unit-sensitive questions
* Table-based questions
* Multi-document comparison questions
* Regulation-condition questions
* Unanswerable questions

The system will be evaluated using:

* Retrieval accuracy
* Citation accuracy
* Answer correctness
* Hallucination rate
* Unit accuracy
* Refusal accuracy
* Table retrieval accuracy

Different RAG configurations will be compared:

```text
Naive vector RAG
Hybrid retrieval RAG
Hybrid retrieval + reranking
Section-aware chunking
Table-aware retrieval
Citation-constrained generation
```

## Current Status

This project is under active development. The current focus is on the document parsing stage, including PDF page parsing, coordinate normalization, table/chart region detection, visual debugging, and manifest generation.

## Expected Deliverables

* Working PDF ingestion pipeline
* Layout-aware parsing output
* Text and table chunking pipeline
* Vector database indexing
* Hybrid retrieval and reranking
* Citation-grounded answer generation
* Evaluation dataset
* Experiment report
* Streamlit demo
* Dockerized deployment

## Future Improvements

* Add chart-aware retrieval for figures and visual evidence.
* Improve table structure reconstruction for irregular AEMO report tables.
* Add workbook-to-PDF numerical cross-validation.
* Support multi-modal RAG over text, tables, charts, and images.
* Build an automated citation verification module.
* Expand evaluation to more AEMO document families and regulatory reports.

