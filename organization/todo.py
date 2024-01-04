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


def create_card_event(queryset):
    d = defaultdict(list)
    for dict_db in queryset:
        t = namedtuple('employees', ['id', 'name'])
        t.id = dict_db.pop('employees__id')
        t.name = dict_db.pop('employees__name')
        d.update(dict_db)
        d[t.__name__].append((t.id, t.name))
    return d


def create_card_record_event(user_id, queryset):

    unique_id_in_queryset = {key['id'] for key in queryset}

    dict_all_records = {}

    for _id in unique_id_in_queryset:
        dict_all_records[_id] = [{k: v for k, v in d.items()} for d in queryset if d['id'] == _id]

    card_records = []

    for list_records in dict_all_records.values():
        dict_record = defaultdict(bool)
        for d in list_records:
            if d.pop('recordings__user__id') == user_id:
                dict_record['recordings__user__id'] = True
            dict_record.update(d)
        if 'recordings__user__id' not in dict_record:
            dict_record['recordings__user__id'] = False
        card_records.append(dict_record)

    return card_records
