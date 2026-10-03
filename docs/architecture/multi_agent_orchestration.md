# Multi-Agent Orchestration & Supervisor Routing

## Orchestration Pattern
VectraBank implements a hierarchical supervisor pattern. The Supervisor analyzes the semantics of user queries and delegates tasks to domain-specialized sub-agents:

```
                  ┌───────────────┐
                  │ Customer User │
                  └───────┬───────┘
                          │ (SSE Stream)
                  ┌───────▼───────┐
                  │  Supervisor   │
                  └──┬───┬───┬───┬┘
       ┌─────────────┘   │   │   └─────────────┐
       ▼                 ▼   ▼                 ▼
┌──────────────┐ ┌─────────┐ ┌────────────┐ ┌───────────────┐
│ Loan Advisor │ │ Compliance │ Investments │ Accounts Spec │
└──────────────┘ └─────────┘ └────────────┘ └───────────────┘
```

## Routing Heuristics
- **Loan Advisor**: Triggers on mortgage, APR, DTI, personal loans, vehicle financing, amortization.
- **Compliance Officer**: Triggers on AML, SAR, wire transfer limits, structuring, OFAC sanctions.
- **Investment Advisor**: Triggers on compound growth, 401(k), index funds, portfolio diversification.
- **Account Specialist**: Triggers on balance inquiry, fee waivers, overdraft, checking/savings tiers.
