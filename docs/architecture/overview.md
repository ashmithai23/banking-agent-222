# VectraBank Architecture Overview

## Executive Summary
VectraBank is an enterprise-grade agentic Retrieval-Augmented Generation (RAG) platform tailored for modern financial institutions. It pairs multi-agent collaborative reasoning with deterministic banking calculation engines and vector search retrieval to provide audited, compliant, and accurate banking assistance.

## Core Architectural Pillars
1. **Multi-Agent Specialist Routing**: Dynamic triage of incoming customer inquiries to specialized agents (Accounts, Loans, Compliance, Investments).
2. **Deterministic Financial Calculation Engines**: Zero-hallucination mathematical execution for debt-to-income (DTI), mortgage affordability, and compound interest.
3. **Hybrid RAG Knowledge Retrieval**: Ingesting bank policies, rate sheets, and disclosures with ChromaDB embeddings.
4. **Real-Time Token Streaming**: Low-latency Server-Sent Events (SSE) delivering immediate token-by-token reasoning feedback to client frontends.
5. **Regulatory & AML Enforcement**: Built-in heuristic and rule-based validation checking for Bank Secrecy Act (BSA) compliance.
