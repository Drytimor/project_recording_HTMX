from collections import defaultdict, namedtuple


def db_function(queryset):
    d = defaultdict(list)
    for dict_db in queryset:
        for k, v in dict_db.items():
            if k == 'employees__name':
                d[k].append(v)
            else:
                d[k] = v
    return d


def card_info_event(queryset):
    d = defaultdict(list)
    for dict_db in queryset:
        t = namedtuple('employees', ['id', 'name'])
        for k, v in dict_db.items():
            if k == 'employees__id':
                t.id = v
            elif k == 'employees__name':
                t.name = v
            else:
                d[k] = v
        d[t.__name__].append((t.id, t.name))
    return d
