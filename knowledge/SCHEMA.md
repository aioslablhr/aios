# AIOS Knowledge Compiler Schema
## Behavioral rules for compiling company knowledge into structured wiki pages

## Page Types

### 1. Concept Pages (`wiki/concepts/`)
A concept is a topic, service, process, or policy the company offers or follows.
- Title is the concept name (e.g. "Flight Booking", "Visa Services")
- Every concept page MUST have:
  - A one-paragraph Description
  - A list of Key Details (bullet points)
  - Related concepts and entities with backlinks
  - Source reference
- Tone: factual, informative, no marketing fluff

### 2. Entity Pages (`wiki/entities/`)
An entity is a named thing — a company, person, location, product, or role.
- Title is the entity name (e.g. "Shin Travels", "UK Tourist Visa")
- Every entity page MUST have:
  - Entity type (Company, Person, Location, Product, Role)
  - Description
  - Key attributes in a table
  - Related concepts and other entities with backlinks
  - Source reference
- Tone: factual, reference-style

### 3. Source Pages (`wiki/sources/`)
A source is a document or origin of information.
- Title is the source name (e.g. "Company Website", "Booking Policy PDF")
- Every source page MUST have:
  - Source type (Website, PDF, Document, API)
  - URL or origin
  - Date retrieved
  - Topics covered (links to concepts)

## Linking Rules
1. Every page MUST have `**Related:**` section with markdown links to related pages
2. Every page MUST have `**Source:**` section with link to its source page
3. Links use relative paths: `[Destinations](../entities/destinations.md)`
4. No broken links — verifiable at compile time
5. No orphan pages — every page must be linked from at least one other page

## Quality Rules
1. No contradictory statements between pages — check existing content before writing
2. No opinions or speculation — only facts from source documents
3. Keep paragraphs short (2-4 sentences max)
4. Use bullet lists for multiple items
5. Dates in ISO format (2026-06-16)
6. Urdu terms get English transliteration in brackets on first use
