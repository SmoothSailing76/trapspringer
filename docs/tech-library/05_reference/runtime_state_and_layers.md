# Runtime State and Layers

Layers are not stored in runtime state.

RuntimeSession contains services. CampaignState contains mutable facts. Save files include state and metadata, not Python service objects.

## Saved

CampaignState, TimeState, PartyState, CharacterStates, ModuleState, KnowledgeState, PublicMap state, audit metadata, content-pack id/version/hash, rules capability snapshot.

## Simple Rule

State is what happened. Layers are how things happen. RuntimeSession connects them.
