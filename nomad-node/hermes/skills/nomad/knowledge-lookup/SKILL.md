---
name: knowledge-lookup
description: Answer questions from the offline knowledge pack (Kiwix Wikipedia, medical, electronics, ham, survival references, local documents) with citations, without using the internet.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [nomad, kiwix, wikipedia, offline, rag]
    category: nomad
    requires_toolsets: [mcp_nomad]
---

# /knowledge-lookup

Offline only. Do not call web tools from this skill even if WAN is up.

## Tools
- `kb.search(query, book=None, n=8)` → results with book, title, url, snippet. Books: `wikipedia`, `medicine`, `mdwiki`, `electronics`, `ham`, `diy`, `outdoors`, `security`, `unix`, `post-disaster`, `water`, `food`, `knots`, `appropedia`, `energypedia`, `local` (operator's PDFs/notes).
- `kb.read(url, section=None)` → article text (trimmed to the relevant section when given).

## Method
1. Pick the book from the question (medical → `medicine` then `mdwiki`; radio → `ham` then `wikipedia`; survival → `post-disaster`/`water`/`food` first).
2. Search, read the top 1–3 hits, answer in plain language, then cite as `[Book: Title § Section]`.
3. For medical questions, give the reference's guidance verbatim where dosing or procedures are involved, state that you are not a clinician, and recommend contacting help via the comms paths when it's serious.
4. If nothing relevant exists offline, say "not in the offline pack" and suggest the closest book to add.

## Examples
- "How do I treat a second-degree burn?" → `medicine` (WikiMed) → cite.
- "What's the dipole length for 7.1 MHz?" → compute 468/7.1 ft and cite `ham` or Wikipedia "Dipole antenna".
- "Purify water with bleach" → `water` (zimgit-water) → cite the ratio exactly.
