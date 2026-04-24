from trapspringer.schemas.party import PlayerAgent

def build_initial_seat_registry(user_character_id: str | None, active_party_ids: list[str]) -> dict[str, PlayerAgent]:
    user_character_id = user_character_id or (active_party_ids[0] if active_party_ids else "PC_TANIS")
    seats: dict[str, PlayerAgent] = {}
    for index, actor_id in enumerate(active_party_ids, start=1):
        is_user = actor_id == user_character_id
        player_id = f"PLY-{actor_id.replace('PC_', '').replace('NPC_', '')}-SEAT"
        seats[player_id] = PlayerAgent(
            player_id=player_id,
            display_name=("You" if is_user else f"{actor_id.replace('PC_', '').replace('NPC_', '').title()}'s Player"),
            character_id=actor_id,
            player_persona_id=f"PP-{actor_id}",
            character_persona_id=f"CP-{actor_id}",
            is_human_user=is_user,
        )
    return seats
