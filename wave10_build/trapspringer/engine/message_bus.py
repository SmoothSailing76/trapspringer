from trapspringer.domain.messages import LayerCommand, LayerEvent, LayerQuery, LayerResult

class MessageBus:
    def make_query(self, from_layer: str, to_layer: str, query_id: str, payload: dict) -> LayerQuery:
        return LayerQuery(from_layer=from_layer, to_layer=to_layer, query_id=query_id, payload=payload)

    def make_command(self, from_layer: str, to_layer: str, command_id: str, payload: dict) -> LayerCommand:
        return LayerCommand(from_layer=from_layer, to_layer=to_layer, command_id=command_id, payload=payload)

    def make_result(self, from_layer: str, to_layer: str, result_id: str, status: str, payload: dict) -> LayerResult:
        return LayerResult(from_layer=from_layer, to_layer=to_layer, result_id=result_id, status=status, payload=payload)

    def make_event(self, from_layer: str, to_layer: str, event_id: str, payload: dict) -> LayerEvent:
        return LayerEvent(from_layer=from_layer, to_layer=to_layer, event_id=event_id, payload=payload)
