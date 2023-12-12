def db_function(queryset):
    lst = []
    for i in queryset:
        d = {}
        id_ = None
        for k, v in i.items():
            if k == 'id':
                id_ = v
            if len(lst) > 0 and id_ == lst[-1]['id']:
                if k != 'employees__name':
                    continue
                else:
                    lst[-1]['employees__name'].append(v)
                    continue
            if k == 'employees__name':
                d1 = {k: [v]}
            else:
                d1 = {k: v}
            d.update(d1)
        if d:
            lst.append(d)
    return lst
