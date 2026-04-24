# Layer 2 — Knowledge-Boundary Layer

Layer 2 controls who knows what, when, and in what form. It separates objective truth, DM-private truth, public tabletop knowledge, actor-private knowledge, and belief.

## Responsibilities

- Fact and belief state.
- Public/private filtering.
- Discovery and propagation.
- Private whispers.
- False belief and deception.
- Content-pack hidden fact seeding.
- Scenario DSL reveal effects.
- API public-state filtering.

## Knowledge Domains

Objective Truth, DM-Private, Public Tabletop, Character-Known, Player-Private, Belief/Misinformation.

## Visibility Classes

`objective_truth`, `dm_private`, `public_table`, `party_known`, `actor_private`, `conditionally_visible`, `inferred_only`, `false_belief`, `forgotten`.

## Example Hidden Fact

```json
{
  "fact_id": "DL1_44F_WICKER_DRAGON_TRUE",
  "proposition": "The apparent dragon in area 44f is wicker.",
  "visibility_class": "dm_private",
  "reveal_triggers": ["inspect_wicker_dragon", "enter_close_range"]
}
```

## Scenario Reveal

```yaml
on_inspect:
  - reveal_fact: DL1_44F_WICKER_DRAGON_TRUE
    to: actor
```

Layer 2 performs the reveal; scripts only request it.

## Invariants

Hidden truth may not be revealed because the engine knows it. Beliefs are not truth. API public state must pass through Layer 2.
