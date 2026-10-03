# Knowledge Chunking & Overlap Strategy

To preserve semantic continuity across financial disclosures:

- **Window Size**: 800 tokens (~3200 characters)
- **Overlap**: 120 tokens (~480 characters)
- **Separators**: Priority order:
  1. `\n## ` (Markdown Headers)
  2. `\n\n` (Paragraph boundaries)
  3. `\n` (Line breaks)
  4. `. ` (Sentence terminal periods)
  5. ` ` (Word boundaries)

This prevents tabular fee schedules or numeric clause boundaries from being severed mid-calculation.
