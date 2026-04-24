from __future__ import annotations


def resolve_rest(request):
    days = int(request.get('days', 1))
    characters = request.get('characters', {})
    mutations = []
    for actor_id, actor in characters.items():
        if getattr(actor, 'current_hp', 0) > 0:
            new_hp = min(getattr(actor, 'max_hp', 0), getattr(actor, 'current_hp', 0) + days)
            mutations.append({'path': f'characters.{actor_id}.current_hp', 'value': new_hp})
    return {'status': 'resolved', 'days': days, 'mutations': mutations, 'notes': 'v0.4 natural healing helper: 1 hp/day baseline.'}
