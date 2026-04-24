# Layer 4 — Table Procedure Layer

Layer 4 controls live flow: setup, travel, exploration, conversation, combat, rest, escape, module events.

## Procedure Loop

1. Determine mode.
2. Present visible situation.
3. Prompt for declarations.
4. Gather user and party declarations.
5. Validate declarations.
6. Resolve legal actions.
7. Commit state.
8. Advance time.
9. Check triggers/transitions.
10. Prompt again or switch mode.

## v0.2.1 Scenario Hooks

`on_enter`, `on_exit`, `on_prompt`, `on_declaration`, `on_validation_failure`, `on_resolution`, `on_round_start`, `on_round_end`, `on_milestone`.

## Transition Validation

Layer 4 validates scene/milestone transitions against the active content pack registry.

## Invariants

No action resolves before declaration and validation. Scenario hooks run only at defined procedure points. Invalid milestone jumps are blocked or reported.
