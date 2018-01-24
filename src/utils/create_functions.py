

def attribution_id(obj, logger):
    if hasattr(obj, "authors") and hasattr(obj, "attribution_date"):
        return obj.authors + '|' + obj.attribution_date.split('-')[0]
    elif hasattr(obj, "authors"):
        return obj.authors
    return None
