def distribute_event_1_positions(graph, party_ids: list[str], hobgoblin_ids: list[str]) -> None:
    for pid in party_ids:
        graph.place(pid, "road_center_party")
    for i, hid in enumerate(hobgoblin_ids):
        graph.place(hid, "left_woodline" if i % 2 == 0 else "right_woodline")
    graph.place("NPC_TOEDE", "toede_front")
