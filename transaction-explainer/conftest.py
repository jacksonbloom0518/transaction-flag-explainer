collect_ignore_glob = []


def pytest_configure(config):
    try:
        config.pluginmanager.set_blocked("langsmith")
    except Exception:
        pass
