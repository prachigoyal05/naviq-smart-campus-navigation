from maps.models import Location

def find_location_from_answer(answer):
    answer = answer.lower()

    locations = Location.objects.all()

    for loc in locations:
        if loc.name.lower() in answer:
            return loc

    return None
