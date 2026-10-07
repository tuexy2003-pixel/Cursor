LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def assert_local_operator_deployment(host: str) -> None:
    if host in LOOPBACK_HOSTS:
        return
    raise RuntimeError(
        "Remote or non-loopback deployment is not supported until operator authentication exists. "
        "Mutation routes currently trust a server-side operator identity only."
    )
