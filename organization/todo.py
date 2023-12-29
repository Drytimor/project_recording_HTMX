from collections import defaultdict


def db_function(queryset):
    d = defaultdict(list)
    for dict_db in queryset:
        for k, v in dict_db.items():
            if k == 'employees__name':
                d[k].append(v)
            else:
                d[k] = v
    return d
