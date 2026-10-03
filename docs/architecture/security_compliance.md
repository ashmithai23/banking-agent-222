# Security & Regulatory Compliance Specification

## Financial Data Safeguards
- **Zero Hardcoded Secrets**: Strict enforcement of runtime `.env` injection.
- **Local Vector Tenancy**: Vector embeddings and documents stored locally in enterprise environments.
- **PII Redaction**: Pre-prompt sanitization filters customer Social Security Numbers (SSN) and 16-digit Primary Account Numbers (PAN).

## AML & Fraud Prevention
- **CTR (Currency Transaction Report)**: Automated trigger on cash or wire transactions exceeding $10,000.00.
- **Structuring Detection**: Pattern detection identifying sub-$10k recurring deposits within 7 business days.
- **Disclaimers**: Mandatory automated regulatory disclosures appended to investment advice (FDIC vs SIPC coverage).
