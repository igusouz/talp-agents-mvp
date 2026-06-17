# Diagrams

This file centralizes the Mermaid diagrams used across the repository documentation.

## System Architecture

```mermaid
flowchart LR
  U[User] --> FE[Frontend Application]
  FE --> ORCH[Workflow Orchestrator]
  ORCH --> INV[Invest Agent]
  ORCH --> COMP[Compliance Agent]
  ORCH --> BDD[BDD QA Agent]
  COMP --> DB[(SQLite)]
  COMP --> CAT[(Compliance Catalog CSV)]
  INV --> LLM[(Google Gemini / LLM Provider)]
  BDD --> LLM
```

## Workflow Sequence

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant F as Frontend
  participant O as Workflow Orchestrator
  participant I as Invest Agent
  participant C as Compliance Agent
  participant B as BDD QA Agent

  U->>F: Submit user story
  F->>O: Start workflow
  O->>I: Analyze story
  I-->>O: INVEST output
  O->>C: Validate INVEST output
  C-->>O: Compliance analysis
  O-->>F: Return analyses
  U->>F: Edit and approve story
  F->>O: Submit approved story
  O->>B: Generate BDD analysis
  B-->>O: BDD output
  O-->>F: Final BDD results
```

## Docker Architecture

```mermaid
flowchart TB
  subgraph Browser
    FE[Frontend Dev Server]
  end

  subgraph Compose[Docker Compose Network]
    ORCH[Workflow Orchestrator]
    COMP[TALP Compliance Agent]
    BDD[TALP BDD QA Agent]
    INV[Invest Agent]
  end

  subgraph Storage
    DB[(SQLite)]
    AUD[(Audit Logs)]
    CAT[(Catalog CSV)]
  end

  FE --> ORCH
  ORCH --> INV
  ORCH --> COMP
  ORCH --> BDD
  COMP --> DB
  COMP --> AUD
  COMP --> CAT
```

## Service Communication

```mermaid
flowchart LR
  FE[Frontend] -->|HTTP| ORCH[Workflow Orchestrator]
  ORCH -->|HTTPX| INV[Invest Agent]
  ORCH -->|HTTPX| COMP[Compliance Agent]
  ORCH -->|HTTPX| BDD[BDD QA Agent]
```

## Human-in-the-Loop Process

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Invest_Analysis: submit story
  Invest_Analysis --> Compliance_Analysis: orchestrator forwards result
  Compliance_Analysis --> Awaiting_Human_Review: analyses ready
  Awaiting_Human_Review --> Awaiting_Human_Review: edit draft
  Awaiting_Human_Review --> BDD_Processing: approve story
  BDD_Processing --> Completed: BDD results returned
  Awaiting_Human_Review --> Draft: rewrite story
  Completed --> [*]
```

## Deployment View

```mermaid
flowchart TB
  subgraph LocalHost[Local Development Host]
    FE[Frontend]
    ORCH[Workflow Orchestrator]
  end

  subgraph Containers[Agent Containers]
    INV[Invest Agent]
    COMP[Compliance Agent]
    BDD[BDD QA Agent]
  end

  FE --> ORCH
  ORCH --> INV
  ORCH --> COMP
  ORCH --> BDD
  COMP --> DB[(SQLite)]
  INV --> LLM[(Google Gemini)]
  BDD --> LLM
```
