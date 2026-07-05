# Card Visual Knowledge Architecture

> Created: 2026-07-04
> Purpose: define the bottom logic layer for AIGC tarot card variants. This layer must understand tarot meaning and market deck grammar before any prompt, image generation, or style variation happens.

## Why This Layer Exists

The previous AIGC architecture had useful outer pieces: visual atoms, style scaffolds, prompt composer, variant metadata, and curation scorecard. But it was missing the deepest layer:

```text
tarot meaning ontology + deck lineage study + market grammar + transformation rules
```

Without this layer, variants would become shallow style remixes. A card image might look interesting but fail as tarot because it would not know which meaning must remain, which symbol may transform, which relation must be visible, and what market category the deck route belongs to.

## Layer Stack

```text
L0 Knowledge Root
  meaning axes
  suit/number/orientation logic
  reference deck studies
  transformation rules

L1 Card Root
  stable card identity: slug, arcana, suit, rank, number, canonical names

L2 Interpretive Facets
  valid meaning routes per card: upright/reversed/context/question bias

L3 Visual Atoms
  symbol atoms, composition atoms, energy/motion atoms

L4 Style Scaffolds
  medium, palette, figure treatment, symbol treatment, border, typography, constraints

L5 Prompt Composer
  structured prompt JSON, not a single opaque prompt string

L6 Generation + Variant Metadata
  model, seed, prompt JSON, image URL, status

L7 Curation
  tarot recognizability, semantic accuracy, transform discipline, deck coherence, originality/safety
```

The new implementation adds L0 as data:

- `backend/app/data/card_visual/meaning_axes.json`
- `backend/app/data/card_visual/reference_decks.json`
- `backend/app/data/card_visual/transformation_rules.json`

And exposes it through:

- `GET /api/card-visuals/knowledge`

## Meaning Axes

Meaning is not stored as a single paragraph. Each card is interpreted through axes:

| Axis | Job |
|---|---|
| card identity | locks the card before variation |
| archetypal function | defines the human pattern being enacted |
| elemental logic | keeps minor arcana tied to suit force |
| numerological stage | gives number/rank developmental structure |
| orientation shadow | makes reversed cards a modulation of the same root |
| relational geometry | turns meaning into spatial composition |
| symbol contract | defines anchor/supporting/optional/forbidden symbols |
| market position | maps the route to a real deck/product expectation |

This means The Fool is not merely "a person on a cliff." It is a threshold archetype with zero-point identity, beginner motion, freedom/risk polarity, edge/traveler anchor contract, and multiple valid transformations.

## Reference Deck Study

Reference decks are study sources, not copy targets. Each deck is stored with:

- lineage
- market role
- visual grammar
- semantic lesson
- variation lesson
- product lesson
- do-not-copy constraints
- source URLs

Initial references:

| Deck | What We Learn |
|---|---|
| Rider-Waite-Smith | narrative minors, readable gesture, symbol atoms, modern tarot grammar |
| Tarot de Marseille | pip logic, historic flat graphic grammar, symbolic simplification |
| Crowley Thoth | correspondence systems, esoteric density, abstract symbolic networks |
| Morgan-Greer | close crop, saturated emotion, RWS readability with stronger immediacy |
| The Wild Unknown | nature/animal metaphor as archetypal replacement |
| Modern Witch | contemporary representation while preserving RWS readability |
| Light Seer's | therapeutic, relatable, light/shadow contemporary archetypes |

The rule is direct: learn from structure, never imitate a living artist, publisher deck, or specific composition.

## Transformation Rules

The lowest layer now defines operational rules:

1. Meaning before style.
2. Preserve at least one anchor symbol or anchor relation.
3. Composition must express relation, not decoration.
4. Learn from decks without imitation.
5. Symbolic density must match the intended audience.
6. Question context may bias the facet but cannot replace the card root.
7. Curation closes the loop and feeds failures back into atom/scaffold design.

These rules should eventually become stronger validation in the prompt composer and generation pipeline.

## Source Notes

Research sources used for the initial reference taxonomy:

- U.S. Games describes Rider-Waite as the recognized influential baseline, originally published in 1909 with Pamela Colman Smith artwork under Arthur Edward Waite's guidance: https://www.usgamesinc.com/rider-waite-tarot-card-deck.html
- U.S. Games describes Thoth as a dense esoteric deck integrating Egyptian mysticism, Qabalah, astrology, alchemy, and ceremonial magic: https://www.usgamesinc.com/crowley-thoth-tarot-deck-small.html
- Tarot de Marseille is used as the historic pip-pattern and Marseille-style reference: https://en.wikipedia.org/wiki/Tarot_of_Marseilles
- Kim Krans notes The Wild Unknown Tarot was hand drawn, self-published in 2012, then released with HarperCollins in 2016: https://kimkrans.com/the-wild-unknown
- Lisa Sterle describes Modern Witch as combining traditional Rider-Waite-Smith symbolism with contemporary characters and objects: https://www.lisasterle.com/mwt
- Hay House describes Light Seer's as reimagining traditional tarot archetypes and symbols in a contemporary, intuitive light/shadow frame: https://www.hayhouse.com/light-seer-s-tarot-card-deck
- U.S. Games describes Morgan-Greer as based on Rider-Waite structure with expressive, saturated imagery: https://www.usgamesinc.com/morgan-greer_tarot_deck.html

## Next Implementation Step

The next technical layer should make prompt composition consult the knowledge root more explicitly:

1. Add `knowledge_context` to generated prompt metadata.
2. Attach selected meaning axes and transformation rules to every variant.
3. Add a validation gate: a prompt cannot be composed if it lacks card identity, facet, anchor contract, composition relation, style scaffold, and do-not-copy constraints.
4. Expand the pilot card data by deriving facets from the knowledge root, not manually writing free-form interpretations.
