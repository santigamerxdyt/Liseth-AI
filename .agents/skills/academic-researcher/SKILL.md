---
name: academic-researcher
description: >
  Search, synthesize, and cite scientific literature from OpenAlex, arXiv, and academic repositories.
  Generates state-of-the-art literature reviews, extracts DOIs, authors, abstracts, and formats
  citations in APA 7th Edition. Essential for university assignments, essays, and thesis research.
license: MIT
metadata:
  version: "1.0.0"
  author: "Liseth AI"
---

# Academic Researcher & Scientific Literature Skill

## Overview
The `academic-researcher` skill equips Liseth with scholarly research capabilities. It queries open academic databases (OpenAlex, arXiv, Europe PMC) without requiring paid API keys, extracting peer-reviewed literature, preprints, citation metrics, and generating formal academic syntheses.

## Core Capabilities
1. **Academic Paper Search (`search`)**:
   - Queries OpenAlex and arXiv for research papers by keyword, concept, or author.
   - Extracts: Title, Authors, Publication Year, Abstract, DOI, Open Access PDF link, and Citation Count.
2. **State of the Art / Literature Review (`literature_review`)**:
   - Synthesizes findings across multiple relevant papers on a given topic.
   - Identifies consensus, debates, methodologies, and research gaps.
3. **APA 7th Edition Citation Generator (`cite_apa`)**:
   - Formats academic references into parenthetical, narrative, and bibliographic formats conforming strictly to APA 7th edition rules.
4. **DOI Resolver (`resolve_doi`)**:
   - Looks up metadata and citation information from a direct DOI identifier.
