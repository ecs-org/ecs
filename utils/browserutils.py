import httpagentparser

SUPPORTED_BROWSERS = {
    'Firefox': 4,
    'Chrome': 12,
    'Safari': 5,
    'Microsoft Internet Explorer': 9,
}

def is_supported_browser(ua):
    try:
        browser = httpagentparser.detect(ua)['browser']
        version = int(browser['version'].split('.', 1)[0])
        name = browser['name']
        for n, v in SUPPORTED_BROWSERS.iteritems():
            if name == n and version >= v:
                return True
    except Exception:
        pass
    return False

def is_malicious_browser(ua):
    try:
        browser = httpagentparser.detect(ua)['browser']
        version = int(browser['version'].split('.', 1)[0])
        name = browser['name']
        for n, v in SUPPORTED_BROWSERS.iteritems():
            if name == n and version < v:
                return True
    except Exception:
        pass
    return False

def is_temporarily_unsupported_browser(ua):
    try:
        browser = httpagentparser.detect(ua)['browser']
        version = int(browser['version'].split('.', 1)[0])
        if name == 'Microsoft Internet Explorer' and version == 9:
            return True
    except Exception:
        pass
    return False
