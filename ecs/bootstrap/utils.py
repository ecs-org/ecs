def update_instance(instance, d):
    changed = False
    for k,v in d.iteritems():
        if not getattr(instance, k) == v:
            setattr(instance, k, v)
            changed = True
    if changed:
        instance.save()
