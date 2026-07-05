# AIGC Tarot Card Visual System Research

> Research date: 2026-07-04
> Goal: build a tarot image-generation system that starts from original tarot roots, decomposes cards into reusable visual atoms, then recombines them through curated style approaches so every card can have meaningful variety without losing tarot recognizability.

## Core Thesis

Do not create one fixed visual prompt per card. That will make the deck feel like a static encyclopedia.

Instead, model each tarot card as:

```text
Card root + meaning facet + symbol atoms + composition atoms + style scaffold + curation route
```

The system should let the same card produce different valid images by changing the selected meaning facet and style scaffold. The variation should be semantic, not random decoration.

Example: The Fool can become a cliff-edge traveler, a threshold of blank light, a seed falling into open air, a childlike geometric zero, or a reckless escape scene. All are valid only if they preserve the core atom: beginning, openness, risk, movement into unknown experience.

## Source Findings

### Historical root

Tarot begins as a card structure before it becomes a divination system. The Morgan Library describes the Visconti-Sforza cards as fifteenth-century Italian cards originally made as a game for aristocratic use, only later associated with occult secrets and fate. The cards were hand-painted luxury objects and are among the most complete surviving fifteenth-century tarot decks.

Implication: the visual system should respect tarot as a designed object: rank, suit, court, trump, materiality, border, and iconography matter. It is not only mystical illustration.

### Marseille root

Tarot de Marseille did not originate in Marseille; it is a French adaptation of Italian decks, with roots around the Italian Renaissance. Marseille became important because card makers spread and stabilized a distinct graphic identity through wood engraving, hand coloring, bright colors, expressive figures, and symbolic simplification.

Implication: style scaffolds should not only imitate painted scenes. They can also use print logic: limited palettes, hard contours, flat symbolic forms, repeated suit pips, and controlled handmade irregularity.

### Waite-Smith root

The Rider-Waite-Smith deck matters because it made the minor arcana narrative and readable. Waite and Pamela Colman Smith created the deck in 1909; Smith's minor arcana drew from older sources such as Sola Busca, Golden Dawn/Etteilla-derived meanings, and her own illustration language. Tarot Heritage notes that RWS became the paradigm through which many modern decks think about tarot.

Implication: RWS should be treated as a semantic reference layer, not a style to copy. We should extract visual atoms from it: actor, prop, gesture, threshold, weather, number, direction, relationship, object placement.

### Original text root

Waite's `The Pictorial Key to the Tarot` is useful because it gives card-level symbolic descriptions and divinatory meanings. For example, The Fool is described through motion, cliff, sky, dog, rose, wand, wallet, sun, and search for experience. The Ace of Wands is a hand from cloud holding a wand, with meanings around creation, beginning, enterprise, and source.

Implication: every card can be decomposed into:

- meaning atoms: beginning, union, burden, rupture, renewal
- symbol atoms: wand, cup, sword, coin, tower, dog, rose, sun
- composition atoms: edge, ascent, fall, exchange, procession, enclosure
- energy atoms: stillness, crossing, eruption, convergence, release

### Atomic design root

Brad Frost's atomic design model breaks systems into atoms, molecules, organisms, templates, and pages. This is meant as a modular design mental model, not just CSS/UI structure.

Implication: use atomic design for image generation:

| Atomic layer | Tarot image generation equivalent |
|---|---|
| Atom | symbol, color note, gesture, element, object, directional force |
| Molecule | meaningful cluster: cliff + open sky + small companion, two cups + exchange gesture |
| Organism | complete card scene or abstract construction |
| Template | deck-level layout: border, title, number, image window, typography |
| Page | final generated card variant with metadata and curation score |

### Text-to-image prompt root

Oppenlaender's taxonomy of prompt modifiers identifies common control layers in text-to-image work: subject terms, image prompts, style modifiers, quality boosters, repeating terms, and magic terms. It also emphasizes that prompt engineering is iterative and controlled through modifiers, weights, and negative constraints.

Implication: our prompt composer should separate subject/meaning from style/quality/negative constraints. A card should not store one prompt string. It should store structured prompt ingredients.

## Atomic Model

### 1. Card Root

The stable identity of the card. This mostly already exists in the current `cards` table.

```ts
CardRoot {
  card_id: string
  slug: string              // major_fool, wands_ace, cups_two
  arcana: 'major' | 'minor'
  suit?: 'wands' | 'cups' | 'swords' | 'pentacles'
  rank?: 'ace' | '2' | ... | 'king'
  number?: number
  canonical_name_zh: string
  canonical_name_en: string
}
```

### 2. Meaning Facet

A card needs multiple meaning facets. Each facet is a valid interpretive route.

```ts
CardMeaningFacet {
  id: string
  card_id: string
  orientation: 'upright' | 'reversed' | 'both'
  context: 'general' | 'love' | 'career' | 'self' | 'decision' | 'spiritual'
  facet_name: string        // beginner's leap, naive risk, sacred union
  core_meaning: string
  emotional_tone: string[]  // hopeful, tense, solemn, tender
  motion: string            // rising, falling, crossing, waiting, breaking
  polarity: string          // expansion/contraction, union/separation
  question_bias?: string    // when auto-selecting visual facet from user question
}
```

### 3. Symbol Atom

Symbols should have transformation permissions. Some are required for recognizability; some can become abstract.

```ts
CardSymbolAtom {
  id: string
  card_id: string
  symbol: string            // cliff, dog, rose, cup, sword, tower
  role: 'anchor' | 'supporting' | 'optional' | 'forbidden'
  abstraction_modes: Array<
    'literal' | 'silhouette' | 'geometry' | 'material' | 'gesture' | 'negative_space'
  >
  meaning_link: string      // why this symbol matters
  replacement_ideas: string[]
}
```

Example: The Fool's cliff can be a literal cliff, a threshold line, a white page edge, a broken map border, or a geometric drop. It should not become a generic mountain if the edge/risk meaning disappears.

### 4. Composition Atom

Composition carries meaning. It should be modeled explicitly.

```ts
CompositionAtom {
  id: string
  card_id: string
  relation_type:
    | 'threshold'
    | 'exchange'
    | 'ascent'
    | 'fall'
    | 'enclosure'
    | 'procession'
    | 'duality'
    | 'radiance'
    | 'fragmentation'
  spatial_rule: string      // figure at edge, two figures facing, object centered
  camera_rule: string       // frontal icon, close object study, distant landscape
  rhythm_rule: string       // symmetrical, unstable, circular, diagonal
}
```

### 5. Style Scaffold

A scaffold is not just a style label. It defines how symbols are transformed.

```ts
StyleScaffold {
  id: string
  name: string
  medium: string
  line_language: string
  palette_logic: string
  figure_treatment: 'human' | 'silhouette' | 'masked' | 'object_only' | 'none'
  symbol_treatment: 'literal' | 'abstract' | 'ornamental' | 'diagrammatic' | 'surreal'
  composition_bias: string
  texture_language: string
  border_system: string
  typography_system: string
  negative_constraints: string[]
}
```

### 6. Generation Route

A route is the curated combination policy. It tells the system what kind of variety to make.

```ts
GenerationRoute {
  id: string
  name: string
  meaning_facet_strategy: string
  scaffold_id: string
  abstraction_level: 0 | 1 | 2 | 3
  tarot_recognizability_target: 1 | 2 | 3 | 4 | 5
  diversity_goal: string
  curation_notes: string
}
```

## Curated Approaches

These are not final deck names. They are reusable creative routes for exploration.

| Route | Meaning focus | Visual behavior | Best for |
|---|---|---|---|
| Canonical Echo | preserve recognizable tarot anchors | keeps 1-3 core symbols literal, varies medium and mood | first generated deck, learning users |
| Archetype Abstract | express the card as a psychological force | turns figures into geometry, thresholds, weather, objects | premium/modern deck |
| Ritual Object | card becomes a talisman or altar object | close-up symbolic still life, crafted materials, inscriptions | collectible cards, share image |
| Emotional Weather | card meaning becomes atmosphere | light, season, pressure, fog, storm, heat, silence | daily draw, mood-led UX |
| Narrative Fragment | one cinematic moment from the card | cropped scene, gesture, unresolved action | interpretation page |
| Diagrammatic Mystic | symbolic map rather than scene | circles, paths, grids, suit objects, constellations | abstract users, advanced readers |
| Material Culture | style comes from craft process | woodcut, textile, ceramic, stained glass, risograph | deck diversity without artist copying |
| Question-Inflected | user question biases the facet | same card changes for love/career/decision/self | personalized AIGC result |

## Designer And Commercial Scope

If PlanetaArcana introduces or sells different designer-led card styles, the style system needs a commercial curation layer. A generated card can be visually interesting but still not be sellable as a deck. Sellable decks need a coherent visual system, clear authorship, rights, quality control, product story, and enough preview material for buyers to trust the work.

Market signals:

- Independent deck marketplaces already position decks by designer identity, deck concept, and category. MakePlayingCards' marketplace lists tarot decks such as architecture/photo-based tarot and highlights top designers, including creators who explicitly position their work as non-AI.
- Brand-led decks can sell as aesthetic objects. The Maker sells a 78-card tarot deck as a collaboration with illustrator Daria Ermolova, explicitly tying the deck to brand patterns, colors, symbols, and a modern lens.
- Crowdfunded tarot decks require more than art: planning, niche research, artist collaboration, prototype assets, pre-launch marketing, campaign management, fulfillment, shipping, and customer support.
- Creator economics can be poor under traditional publishing. Public creator writeups estimate low per-deck royalties and emphasize that self-publishing can produce better margins only if the creator can handle production, marketing, quality control, and fulfillment.
- Publishing/artist contracts are a risk area. Artist compensation, royalties, advance earn-out, alteration rights, merch rights, and ownership must be explicit before selling designer styles.

### Sellable Scope Levels

Use scope levels so we can curate progressively instead of pretending every style is ready for a full 78-card commercial deck.

| Scope | Card coverage | Purpose | Gate |
|---|---:|---|---|
| Style Probe | 3-5 cards | test one scaffold quickly | meaning survives style transformation |
| Pilot Set | 10 cards | test range across archetypes | works across light/dark, major/minor, figure/object scenes |
| Major Arcana Set | 22 cards | first collectible/digital product | coherent trump journey and title/border system |
| Full Deck Candidate | 78 cards + back | full tarot completeness | suits, courts, majors all distinct but unified |
| Sellable Edition | 78 + guidebook + box/product copy | commercial release | rights, print specs, QA, previews, pricing, support plan |

### Designer Style Submission Baseline

Each designer or designer-like AIGC route should be submitted as a structured scaffold, not a moodboard alone.

```ts
DesignerStyleSubmission {
  designer_id?: string
  style_scaffold_id: string
  title: string
  authorship_model: 'human' | 'human_ai_collab' | 'ai_generated_curated'
  concept_statement: string
  target_buyer: string
  visual_language: string
  palette_tokens: string[]
  material_process: string[]
  symbol_rules: string
  forbidden_motifs: string[]
  typography_direction: string
  card_back_direction: string
  sample_cards: string[]        // required card ids
  rights_statement: string
  ai_disclosure: string
  commercial_permissions: string[]
}
```

Minimum sample cards for style evaluation:

```text
The Fool, High Priestess, Lovers, Death, Tower,
Star, Ace of Wands, Two of Cups, Seven of Swords, Ten of Pentacles
```

These cards test innocence, secrecy, intimacy, transformation, rupture, hope, ignition, reciprocity, ambiguity, and material legacy.

### Commercial Curation Baseline

Score every designer route before it becomes sellable.

| Criterion | Question | Minimum |
|---|---|---:|
| Tarot integrity | Do cards preserve core meanings and enough recognizability? | 4/5 |
| Style coherence | Does the deck feel like one designed system? | 4/5 |
| Range | Can the style handle soft, violent, sacred, comic, abstract, and mundane cards? | 4/5 |
| Product story | Can we explain why this deck exists in one paragraph? | 4/5 |
| Originality | Does it avoid copying modern decks, living artists, or protected IP? | 5/5 |
| Rights readiness | Do we have clear commercial permission and AI disclosure? | 5/5 |
| Print readiness | Are dimensions, bleed, contrast, and title legibility acceptable? | 4/5 |
| Buyer preview | Are enough cards visible for a buyer to trust the deck? | 4/5 |

Sellable threshold:

```text
no criterion below minimum
average score >= 4.4
rights_readiness == 5
originality == 5
```

### Product Presentation Baseline

For each sellable designer style, the product page should include:

- designer/style name
- authorship label: human, human + AI, or AI-generated curated
- one-sentence deck promise
- 10-12 card previews before purchase
- explanation of the visual system: symbols, palette, composition, material process
- whether it follows RWS, Marseille, Thoth-inspired, or original symbolic mapping
- included assets: physical deck, digital deck, guidebook, card back, box
- usage rights: personal reading, commercial reader use, redistribution limits
- AI disclosure and human curation statement

### Rights And Ethics Baseline

Before selling, require:

- written ownership or license for final images
- clear rights for physical cards, digital cards, marketing images, merchandise, translations, and future editions
- attribution rules for human designers
- royalty or flat-fee terms
- AI model/provider usage compliance
- no direct living-artist style mimicry
- no copied modern tarot deck composition as the primary image structure
- no sacred-cultural motifs used as decoration without context and permission
- documented source layer: public-domain root, original designer input, generated variants, final human edits

This is especially important because card decks are artwork-heavy products. A weak rights model will become a product risk once the deck has buyers, creators, affiliates, and physical inventory.

## Initial Example Atoms

### The Fool

Root meaning: beginning, openness, risk, unspent potential, movement into unknown experience.

Meaning facets:

| Facet | Tone | Composition | Symbol anchors |
|---|---|---|---|
| Beginner's leap | bright, open | figure or force at threshold | cliff/edge, open sky, light |
| Naive risk | playful, unstable | diagonal imbalance | small companion, loose bundle, exposed edge |
| Zero point | quiet, abstract | circular void or blank horizon | zero/circle, threshold, sunrise |
| Spirit seeking experience | mythic, airy | upward gaze, path beyond frame | sun, travel object, distant world |
| Reversed recklessness | tense, overexposed | falling/cropping/tilt | broken path, ignored companion, unstable ground |

Prompt ingredient example:

```text
card_root: The Fool
facet: zero point / infinite potential
symbols: threshold edge, white sun, small travel bundle, circular zero motif
composition: figure reduced to silhouette, suspended before an open horizon
scaffold: Diagrammatic Mystic
negative: no clown costume, no modern playing card joker, no copied Rider-Waite composition
```

### Two of Cups

Root meaning: mutual recognition, emotional exchange, alliance, attraction, chosen reciprocity.

Meaning facets:

| Facet | Tone | Composition | Symbol anchors |
|---|---|---|---|
| Sacred exchange | tender, formal | two vessels meeting | two cups, balanced hands |
| Emotional contract | intimate, grounded | mirrored figures or objects | paired vessels, crossing line |
| Healing union | calm, luminous | shared center | water, soft symmetry |
| Unequal bond | uneasy | one cup fuller/heavier | imbalance, broken symmetry |

### Ace of Wands

Root meaning: ignition, creative source, enterprise, beginning of will.

Meaning facets:

| Facet | Tone | Composition | Symbol anchors |
|---|---|---|---|
| Creative spark | energetic | single vertical object emerging | wand, flame/sprout, cloud/hand/source |
| New enterprise | decisive | object pointing forward | wand, road, first mark |
| Raw life force | primal | branch as living force | green shoot, fire color, upward motion |
| Burnout seed | reversed | blocked ignition | smoke, broken branch, dim ember |

## Curation Criteria

Every generated card variant should be reviewed against five questions:

1. **Tarot recognizability**: can a tarot-literate user infer the card without reading the title?
2. **Semantic accuracy**: does the image express the chosen facet, not just the card name?
3. **Transform discipline**: were required anchors preserved or meaningfully abstracted?
4. **Deck coherence**: does it belong to the selected scaffold?
5. **Originality and safety**: does it avoid copying living artists, protected modern decks, sacred-cultural decoration without context, and generic fantasy tropes?

Use a 1-5 score per criterion. A variant needs at least:

```text
recognizability >= 3
semantic_accuracy >= 4
deck_coherence >= 4
originality_safety >= 5
```

For abstract routes, recognizability can be lower only if title, border, and symbol atoms make the card usable in-product.

## Proposed Data Model

Current table `cards` can stay as the canonical reading source. Add visual-generation tables around it.

```text
cards
  existing 78-card canonical data

card_visual_facets
  id
  card_id
  orientation
  context
  facet_name
  core_meaning
  emotional_tone_json
  motion
  polarity
  question_bias

card_symbol_atoms
  id
  card_id
  symbol
  role
  abstraction_modes_json
  meaning_link
  replacement_ideas_json

card_composition_atoms
  id
  card_id
  relation_type
  spatial_rule
  camera_rule
  rhythm_rule

style_scaffolds
  id
  name
  medium
  line_language
  palette_logic
  figure_treatment
  symbol_treatment
  composition_bias
  texture_language
  border_system
  typography_system
  negative_constraints_json

generation_routes
  id
  name
  scaffold_id
  meaning_facet_strategy
  abstraction_level
  recognizability_target
  diversity_goal
  curation_notes

generated_card_variants
  id
  card_id
  facet_id
  route_id
  prompt_json
  image_url
  model
  seed
  curation_scores_json
  status
```

## Prompt Composer Contract

The composer should produce structured prompts, not only text.

```ts
GeneratedPrompt {
  subject_terms: string[]
  meaning_terms: string[]
  required_symbols: string[]
  transformed_symbols: string[]
  composition_terms: string[]
  style_modifiers: string[]
  quality_modifiers: string[]
  negative_constraints: string[]
  title_text?: string
}
```

This matches text-to-image research better than a single handcrafted sentence because it lets us test which layer changes the image.

## Recommended Build Order

1. **Create the visual schema as data files first**
   - Start with JSON/YAML under `backend/app/data/card_visual/`.
   - Avoid DB migration until the taxonomy proves stable.

2. **Seed 10-card pilot**
   - The Fool, Magician, High Priestess, Lovers, Death, Tower, Star, Ace of Wands, Two of Cups, Ten of Swords.
   - These cover beginning, agency, intuition, union, transformation, rupture, hope, ignition, reciprocity, and collapse.

3. **Define 4 style scaffolds**
   - Canonical Echo
   - Archetype Abstract
   - Ritual Object
   - Emotional Weather

4. **Build prompt composer**
   - Input: `card_id`, optional `question`, optional `route_id`, optional `orientation`.
   - Output: structured prompt + final text prompt.

5. **Generate and curate small batches**
   - 10 cards x 4 routes x 2 variants = 80 images.
   - Score them before scaling to all 78.

6. **Only then connect to UI**
   - Flip/card visuals should consume curated assets, not unstable prompt experiments.

7. **Add commercial curation after visual pilot**
   - Do not sell the first generated images.
   - First sellable target should be a 22-card Major Arcana digital/prototype edition or a 10-card style preview pack.
   - Full 78-card products should wait until the route passes commercial curation and rights review.

## Implementation Notes For PlanetaArcana

- Keep reading meanings and image-generation semantics separate. A reading prompt wants interpretive clarity; an image prompt wants visual anchors and constraints.
- Add `slug` to `cards` before asset work. Stable slugs are necessary for image paths and variant metadata.
- Do not store generated prompts inside `cards`; prompts evolve faster than card identity.
- Treat style scaffolds as product content, not code constants. Designers should be able to add/retire scaffolds without editing core reading logic.
- Avoid named living artist style prompts. Use medium, process, composition, and material language instead.
- Treat designer style routes as possible products. Add author, rights, disclosure, preview, and sellability fields before marketplace work.

## Sources

- Morgan Library & Museum, Visconti-Sforza Tarot Cards: https://www.themorgan.org/collection/tarot-cards
- Marseille Tourism, Le Tarot de Marseille: https://www.marseille-tourisme.com/en/discover-marseille/traditions/the-tarot-of-marseille/
- Tarot Heritage, The Rider Waite Smith Deck: https://tarot-heritage.com/history-4/the-rider-waite-smith-deck/
- A. E. Waite, `The Pictorial Key to the Tarot`, Internet Sacred Text Archive: https://sacred-texts.com/tarot/pkt/index.htm
- A. E. Waite, `The Pictorial Key to the Tarot`, Wikisource public-domain note: https://en.wikisource.org/wiki/The_Pictorial_Key_to_the_Tarot
- Brad Frost, Atomic Design methodology: https://atomicdesign.bradfrost.com/chapter-2/
- Jonas Oppenlaender, `A Taxonomy of Prompt Modifiers for Text-To-Image Generation`: https://arxiv.org/html/2204.13988v3
- MakePlayingCards marketplace, self-published card designs: https://www.makeplayingcards.com/marketplace/index.aspx
- The Maker Shop, 78-card tarot deck artist collaboration: https://shop.themaker.com/products/tarot-deck
- PledgeBox, creator guide to launching Kickstarter tarot decks: https://www.pledgebox.com/post/kickstarter-tarot-decks
- Benebell Wen, self-publishing vs. traditional publishing deck economics: https://benebellwen.com/2020/06/25/show-me-the-numbers-self-publishing-vs-traditional-publishing-of-a-tarot-oracle-deck/
- Benebell Wen, self-publishing tarot deck costs: https://benebellwen.com/2018/09/12/what-does-it-cost-to-self-publish-a-tarot-deck/
- Jane Friedman, creator protection in publishing deals: https://janefriedman.com/good-intentions-arent-enough-in-publishing-deals-how-creators-can-protect-themselves/
- RGD, Designer Collector: Tarot Decks: https://rgd.ca/articles/designer-collector-tarot-decks
