def get_backoff(attempts: int) -> int:
    return min(60, 2 ** attempts)


