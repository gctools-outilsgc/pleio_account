from constance import config, settings


def app(request):
    # Pre-load all of the settings under Customizations using a single
    # efficient operation, since some (ex: APP_TITLE) are used dozens of times
    # in a standard template.
    return {
        'app': dict(config._backend.mget(
            k for k in settings.CONFIG.keys()
            if k.startswith('APP_')
        ))
    }
