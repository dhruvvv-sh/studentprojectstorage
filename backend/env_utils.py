import os


def env_first(*names, default=None, required=False, required_message=None):
    """
    Return the first non-empty environment variable value from `names`.

    Variables are checked left-to-right to preserve precedence. If no value is
    found, `default` is returned unless `required=True`, in which case a
    ValueError is raised. Use `required_message` to provide a custom error text.
    """
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    if required:
        if required_message:
            raise ValueError(required_message)
        raise ValueError(f"Missing required environment variable. Set one of: {', '.join(names)}")
    return default
