# PlanetaArcana Development Workflow

> Updated: 2026-07-04
> Purpose: turn the current roadmap, competitor research, and AIGC card-visual research into an executable development order.

## Current State

The product has already completed the defensive and retention foundation:

- Phase 1.5 core stability and cost protection is done.
- Phase 2 account/history/daily draw/quota/share bonus foundation is done.
- Phase 3 experience depth is partially done:
  - streaming initial interpretation is done
  - persona-based readings are done
  - single-card and two-choice spreads are done
  - AI auto spread selection is done
  - flip/card visuals, share card, and PWA/push are still open
- Phase 4 AIGC visual foundation is now partially implemented:
  - bottom tarot knowledge layer is now defined
  - 78 card slugs are seeded and backfilled
  - 10 pilot cards have facets, symbols, and composition atoms
  - four style scaffolds are defined
  - prompt composer, variant metadata, internal Visual Lab, and curation scorecard are done
  - actual image generation batches and human curation are still open

The new AIGC direction adds one important constraint: card visuals should not be implemented as generic placeholders or one fixed prompt per card. Visual work needs a semantic atom system first.

## Development Order

| Order | Phase | Status | Main Output | Release Gate |
|---:|---|---|---|---|
| 1 | Core Stability | Done | reliable interpretation, quota, tests | backend tests pass |
| 2 | Retention Foundation | Done | auth, history, daily draw, quota/share bonus | account and quota flows pass |
| 3A | Low-Friction Reading UX | Done | AI auto spread selection | user can ask without choosing spread manually |
| 3B | Reading UX Polish | Optional | Celtic Cross decision, follow-up streaming if needed | no regression in interpretation flow |
| 4A | AIGC Visual Data Foundation | Done | knowledge root, card slugs, visual atoms, style scaffolds, prompt composer | 10-card pilot produces structured prompts |
| 4B | Curated Card Visual Pilot | In progress | Visual Lab, variant metadata, scorecard, generated/curated variants | variants pass semantic and style scorecard |
| 4C | Card Visual UI | After 4B | flip animation and curated card assets | mobile/desktop visual smoke test passes |
| 5A | Share Growth Loop | After 4C | share card image tied to share +1 quota | share image is trackable and quota-safe |
| 5B | PWA Retention Loop | After 5A | install flow and reminders | opt-in reminders work and can be disabled |
| 6 | Designer/Commercial Decks | Later | sellable style packs or deck editions | rights, preview, pricing, QA gates pass |

## Completed Sprint: Phase 3A

**AI auto spread selection** is implemented before visual-generation work.

Why:

- It directly reduces reading friction.
- It uses existing spread infrastructure.
- It is small enough to ship before the larger AIGC pipeline.
- It gives later AIGC work better context because the question can influence both spread and visual facet.

### 3A Workflow

1. Backend scope
   - Add a spread recommendation contract: input `question_text`, optional `intent/options`; output `spread_type`, `reason`, and fallback confidence.
   - Supported MVP choices: `single`, `past_present_future`, `two_choice`.
   - Keep Celtic Cross out of auto-selection until layout/cost is ready.

2. Backend implementation
   - Add service/helper near `backend/app/services/ai/`.
   - Add endpoint, likely `POST /api/spreads/recommend`.
   - Use deterministic fallback rules if AI is unavailable.
   - Never consume full interpretation quota for recommendation unless we intentionally decide it is an AI-cost event.

3. Frontend implementation
   - Make "let PlanetaArcana choose" the default spread mode.
   - Show the selected spread and short reason before drawing or at the draw step.
   - Preserve manual spread selection for users who want control.

4. Tests
   - Backend tests for recommendation success, fallback, invalid two-choice input, and no spread-count mismatch.
   - Frontend smoke test for auto mode and manual mode.

5. Release gate
   - A user can enter only a question, draw cards, and reach streaming interpretation without manually choosing a spread.

Verification:

- `pytest backend/tests/test_spreads.py`
- `pytest backend/tests`
- `npm run build`

Known setup gap:

- `npm run lint` does not run because the frontend has no ESLint configuration file.

## Phase 4A: AIGC Visual Data Foundation

Do this before flip/card visuals.

### 4A Workflow

0. Add bottom knowledge root
   - `meaning_axes.json`: tarot logic axes such as card identity, archetypal function, suit logic, number logic, orientation shadow, relational geometry, symbol contract, market position.
   - `reference_decks.json`: market/reference deck studies with lineage, visual grammar, semantic lesson, variation lesson, product lesson, source URLs, and do-not-copy constraints.
   - `transformation_rules.json`: operational rules that prevent shallow style remixing.
   - `GET /api/card-visuals/knowledge` exposes this layer for tooling.

1. Add stable card slugs
   - Extend `cards` with `slug`.
   - Seed deterministic slugs such as `major_fool`, `wands_ace`, `cups_two`.
   - Update schemas/types/API responses.

2. Create data-first visual taxonomy
   - Start with files under `backend/app/data/card_visual/`.
   - Do not add database tables until the taxonomy survives a pilot.
   - Pilot cards: Fool, Magician, High Priestess, Lovers, Death, Tower, Star, Ace of Wands, Two of Cups, Ten of Swords.

3. Add visual atom files
   - `facets.json`: multiple meaning facets per pilot card.
   - `symbols.json`: required/supporting/optional/forbidden symbols.
   - `compositions.json`: spatial and rhythm rules.
   - `style_scaffolds.json`: Canonical Echo, Archetype Abstract, Ritual Object, Emotional Weather.

4. Build prompt composer
   - Input: card slug, route, orientation, optional question context.
   - Output: structured prompt JSON plus final text prompt.
   - Keep image-generation prompts separate from reading prompts.

5. Tests
   - Validate every pilot card has at least 3 facets, 3 symbol atoms, and 1 composition rule.
   - Validate every style scaffold has negative constraints and symbol-treatment rules.
   - Snapshot-test generated prompt structure.

6. Release gate
   - For each pilot card and scaffold, the system can generate a structured prompt without touching the reading flow.

Verification:

- `pytest backend/tests/test_card_visual_data.py backend/tests/test_card_visual_prompts.py`
- `pytest backend/tests`
- `npm run build`

## Phase 4B: Curated Card Visual Pilot

This phase is mostly curation and quality control. The internal Visual Lab exists only to make prompt generation, variant drafting, and score submission repeatable.

Completed tooling:

- `GET /api/card-visuals/catalog`
- `POST /api/card-visuals/prompts`
- `POST /api/card-visuals/variants`
- `GET /api/card-visuals/variants`
- `PATCH /api/card-visuals/variants/{id}`
- `POST /api/card-visuals/variants/{id}/curation`
- Frontend `/visual-lab`

### 4B Workflow

1. Generate small batches
   - 10 pilot cards x 4 scaffolds x 2 variants = 80 images max.
   - Keep metadata: model, seed, route, prompt JSON, date, reviewer.

2. Score variants
   - Tarot recognizability.
   - Semantic accuracy.
   - Transform discipline.
   - Deck coherence.
   - Originality/safety.
   - The backend scorecard validates every score from 1 to 5 and writes `approved`, `needs_revision`, or `rejected`.

3. Select usable variants
   - Each scaffold should pass at least 7 of 10 pilot cards before expanding.
   - Reject styles that only work for pretty or atmospheric cards.

4. Release gate
   - At least one scaffold has curated usable variants for the 10-card pilot.

## Phase 4C: Card Visual UI

Only build flip/card visuals after curated pilot assets exist.

### 4C Workflow

1. Asset contract
   - Use card slug and variant metadata for image lookup.
   - Support fallback image when no curated variant exists.

2. UI implementation
   - Flip animation reads existing drawn-card data.
   - Animation must not change draw result, orientation, or persisted interpretation data.
   - Card layout must work for 1-card, 2-card, 3-card, and future 10-card spreads.

3. Verification
   - Desktop and mobile smoke test.
   - Check reversed cards, loading states, missing image fallback, and streaming interpretation page.

4. Release gate
   - Reading flow feels visual without breaking interpretation reliability.

## Phase 5A: Share Growth Loop

Build share image after card visuals have a stable asset contract.

### 5A Workflow

1. Generate share card image
   - Include app brand, question summary, selected cards, and share URL.
   - Avoid exposing private full interpretation by default.

2. Connect existing share bonus
   - Keep `POST /divines/{id}/share` as the quota grant authority.
   - Add referral/tracking parameter separate from quota grant.

3. Release gate
   - User can share a visual result card and receive the existing +1 quota safely once per eligible divine.

## Phase 5B: PWA Retention Loop

PWA should come after daily draw and share loops are useful.

### 5B Workflow

1. Installability
   - Manifest, icons, service worker, offline fallback.

2. Notification consent
   - Daily draw reminder.
   - Three-day follow-up reminder.
   - Clear unsubscribe path.

3. Release gate
   - PWA install works and reminders are opt-in, testable, and reversible.

## Phase 6: Designer And Commercial Decks

Do not build commerce before the visual pipeline can produce curated, rights-safe sets.

### 6 Workflow

1. Designer submission model
   - Capture authorship model, rights statement, AI disclosure, style scaffold, sample cards, and commercial permissions.

2. Product readiness
   - Start with a 10-card style preview pack or 22-card Major Arcana prototype.
   - Do not sell full 78-card decks until a full curation and rights review passes.

3. Commerce prerequisites
   - Pricing, refund policy, license terms, product page previews, print/digital asset QA.

4. Release gate
   - Sellable deck route passes commercial curation, originality, rights, and preview gates.

## Default Feature Workflow

Every feature should move through the same loop:

1. Scope the user flow, data ownership, cost risk, and success event.
2. Implement backend contract first when state or AI cost is involved.
3. Add focused backend tests for success, validation, permission, quota/cost, and fallback paths.
4. Implement frontend using existing UI patterns.
5. Run backend tests and a manual frontend smoke test.
6. Update docs if the feature changes roadmap, data model, or release gates.

## Not Now

- Full 78-card generated deck before the 10-card pilot passes.
- Marketplace or payment flow before rights/commercial curation exists.
- Physical printing or fulfillment.
- One fixed prompt per card.
- Named living-artist style prompts.
- PWA push before share/daily draw loops are worth reminding users about.
- Celtic Cross before layout, cost, and interpretation quality are designed.
