from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Location, Edge
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # you should NOT use csrf_exempt in prod
import json
from .models import Location, Edge
import json
from django.http import JsonResponse
import heapq


@require_GET
def locations_list(request):
    """
    Return all locations for the dropdowns.
    """
    locations = list(Location.objects.values('id', 'name', 'code', 'x', 'y', 'floor'))

    return JsonResponse({'locations': locations})


def build_graph():
    """
    Build adjacency list graph from Location & Edge models.
    {location_id: [(neighbor_id, distance), ...]}
    """
    graph = {}

    for loc in Location.objects.all():
        graph[loc.id] = []

    for edge in Edge.objects.select_related('from_location', 'to_location'):
        graph[edge.from_location_id].append((edge.to_location_id, edge.distance))
        if edge.bidirectional:
            graph[edge.to_location_id].append((edge.from_location_id, edge.distance))

    return graph


def dijkstra(graph, start_id, end_id):
    """
    Standard Dijkstra shortest path.
    """
    INF = float('inf')
    dist = {node: INF for node in graph}
    prev = {node: None for node in graph}

    dist[start_id] = 0
    heap = [(0, start_id)]

    while heap:
        current_dist, node = heapq.heappop(heap)
        if current_dist > dist[node]:
            continue

        if node == end_id:
            break

        for neighbor, weight in graph.get(node, []):
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(heap, (new_dist, neighbor))

    # reconstruct path
    path = []
    cur = end_id
    if dist[end_id] == INF:
        return [], INF

    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path, dist[end_id]


@require_GET
def shortest_route(request):
    """
    API: /maps/route/?start=ID&end=ID
    Returns path (list of locations) and total distance.
    """
    start = request.GET.get('start')
    end = request.GET.get('end')

    if not start or not end:
        return JsonResponse(
            {'error': 'start and end parameters are required'},
            status=400
        )

    try:
        start_id = int(start)
        end_id = int(end)
    except ValueError:
        return JsonResponse({'error': 'Invalid start or end id'}, status=400)

    graph = build_graph()
    if start_id not in graph or end_id not in graph:
        return JsonResponse({'error': 'Start or end location not found'}, status=404)

    path_ids, total_distance = dijkstra(graph, start_id, end_id)

    if not path_ids:
        return JsonResponse({'error': 'No route found'}, status=404)

    locations_map = {loc.id: loc for loc in Location.objects.filter(id__in=path_ids)}
    path_detail = [
        {
            'id': loc_id,
            'name': locations_map[loc_id].name,
            'code': locations_map[loc_id].code,
            'x': float(locations_map[loc_id].x),
            'y': float(locations_map[loc_id].y),
            'floor': locations_map[loc_id].floor,
        }
        for loc_id in path_ids
    ]

    return JsonResponse({
        'path': path_detail,
        'total_distance': round(total_distance, 2),
    })

@csrf_exempt   # for quick dev; replace with proper CSRF if you use tokens
@require_POST
def add_node(request):
    """
    Expects JSON: { name, code, x, y, floor }
    x,y should be image-space coordinates (floats)
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        name = payload.get('name')
        code = payload.get('code') or ''
        x = float(payload.get('x') or 0)
        y = float(payload.get('y') or 0)
        floor = payload.get('floor') or ''
        if not name:
            return JsonResponse({'success': False, 'error': 'Name required'}, status=400)
        loc = Location.objects.create(name=name, code=code, x=x, y=y, floor=floor)
        return JsonResponse({'success': True, 'id': loc.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def add_edge(request):
    """
    Expects JSON: { from_id, to_id, distance }
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        f = int(payload.get('from_id'))
        t = int(payload.get('to_id'))
        dist = float(payload.get('distance') or 0)
        # create bidirectional edge
        a = Location.objects.get(id=f)
        b = Location.objects.get(id=t)
        edge = Edge.objects.create(from_location=a, to_location=b, distance=dist, bidirectional=True)
        return JsonResponse({'success': True, 'id': edge.id})
    except Location.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Location not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def edges_list(request):
    """
    Returns edges for drawing on canvas:
    { edges: [ {id, from_location, to_location, distance}, ... ] }
    """
    eds = list(Edge.objects.values('id', 'from_location', 'to_location', 'distance'))
    return JsonResponse({'edges': eds})

# decorator that requires login + superuser
def superuser_required(view_func):
    decorated = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated

# Example: secure add_node (replace your current add_node)
@require_POST
@superuser_required
def add_node(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    name = (payload.get('name') or '').strip()
    code = (payload.get('code') or '').strip()
    floor = (payload.get('floor') or '').strip()
    try:
        x = float(payload.get('x', 0))
        y = float(payload.get('y', 0))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid coordinates'}, status=400)

    if not name:
        return JsonResponse({'success': False, 'error': 'Name is required'}, status=400)

    # auto-generate code if empty (same logic as earlier)
    if not code:
        base = "".join([c for c in name.upper() if c.isalnum()])[:6] or "LOC"
        code_candidate = base
        suffix = 1
        while Location.objects.filter(code=code_candidate).exists():
            code_candidate = f"{base}{suffix}"
            suffix += 1
        code = code_candidate

    if Location.objects.filter(code=code).exists():
        return JsonResponse({'success': False, 'error': 'Node code already exists.'}, status=400)

    loc = Location.objects.create(name=name, code=code, x=x, y=y, floor=floor)
    return JsonResponse({'success': True, 'id': loc.id, 'code': loc.code})

# Example: secure add_edge (if you have it)
@require_POST
@superuser_required
def add_edge(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    try:
        a = int(payload.get('from_id'))
        b = int(payload.get('to_id'))
        dist = float(payload.get('distance', 0))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid input'}, status=400)

    # optional: validate nodes exist
    if not Location.objects.filter(id=a).exists() or not Location.objects.filter(id=b).exists():
        return JsonResponse({'success': False, 'error': 'Invalid node id(s)'}, status=400)

    edge = Edge.objects.create(from_location_id=a, to_location_id=b, distance=dist, bidirectional=True)
    return JsonResponse({'success': True, 'id': edge.id})

# NEW: update_node view to persist dragged coords (superuser only)
@require_POST
@superuser_required
def update_node(request):
    """
    Expects JSON: { id: <node id>, x: <image-space x>, y: <image-space y> }
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    try:
        node_id = int(payload.get('id'))
        x = float(payload.get('x'))
        y = float(payload.get('y'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid id or coordinates'}, status=400)

    try:
        loc = Location.objects.get(id=node_id)
    except Location.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Location not found'}, status=404)

    loc.x = x
    loc.y = y
    loc.save(update_fields=['x','y'])

    return JsonResponse({'success': True, 'id': loc.id, 'x': loc.x, 'y': loc.y})

@csrf_exempt
def resolve_qr_location(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    qr_data = body.get("qr_data", "")

    # ✅ Normalize QR data (CRITICAL)
    qr_data = (
        qr_data
        .strip()
        .replace('"', '')
        .replace("'", '')
        .upper()
    )

    print("FINAL QR STRING:", repr(qr_data))

    # ✅ Accept if it contains NQ:
    if "NQ:" not in qr_data:
        return JsonResponse({"error": "Invalid QR format"}, status=400)

    code = qr_data.split("NQ:", 1)[1].strip()

    print("EXTRACTED CODE:", repr(code))

    try:
        location = Location.objects.get(code=code)
    except Location.DoesNotExist:
        return JsonResponse({"error": "Unknown location"}, status=404)

    return JsonResponse({
        "location": {
            "id": location.id,
            "name": location.name,
            "code": location.code,
            "x": location.x,
            "y": location.y,
            "floor": location.floor
        }
    })