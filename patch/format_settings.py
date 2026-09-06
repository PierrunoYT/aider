import re

# Argument and variable names whose values are credentials
SECRET_NAME = re.compile(r"(key|token|secret|password|passwd|credential)", re.IGNORECASE)

# A shorter --set-env value is not a credential, and blanking it everywhere
# would mangle unrelated output
MIN_SECRET_LENGTH = 8


def is_secret_name(name):
    return bool(SECRET_NAME.search(str(name)))


def mask_secret(value):
    """Keep only the last four characters of a secret."""

    value = str(value)
    if len(value) <= 4:
        return "..."

    return f"...{value[-4:]}"


def mask_setting(setting):
    """Mask the value side of a NAME=VALUE argument, such as --api-key."""

    name, sep, value = str(setting).partition("=")
    if not sep or not value:
        return setting

    return f"{name}={mask_secret(value)}"


def get_secret_values(args):
    """Every value in the arguments that must not be printed or logged."""

    values = []

    for name, value in vars(args).items():
        if isinstance(value, str) and value and is_secret_name(name):
            values.append(value)

    for setting in getattr(args, "api_key", None) or []:
        _, sep, value = str(setting).partition("=")
        if sep and value:
            values.append(value)

    for setting in getattr(args, "set_env", None) or []:
        name, sep, value = str(setting).partition("=")
        if sep and value and (is_secret_name(name) or len(value) >= MIN_SECRET_LENGTH):
            values.append(value)

    # Longest first, so one secret containing another is masked whole
    return sorted(set(values), key=len, reverse=True)


def scrub_sensitive_info(args, text):
    # Replace sensitive information with last 4 characters
    if not text:
        return text

    for value in get_secret_values(args):
        text = text.replace(value, mask_secret(value))

    return text


def format_settings(parser, args):
    show = scrub_sensitive_info(args, parser.format_values())
    # clean up the headings for consistency w/ new lines
    heading_env = "Environment Variables:"
    heading_defaults = "Defaults:"
    if heading_env in show:
        show = show.replace(heading_env, "\n" + heading_env)
        show = show.replace(heading_defaults, "\n" + heading_defaults)
    show += "\n"
    show += "Option settings:\n"
    for arg, val in sorted(vars(args).items()):
        if val:
            if arg in ("api_key", "set_env") and isinstance(val, list):
                # These carry NAME=VALUE pairs, so mask every value side
                val = [mask_setting(setting) for setting in val]
            val = scrub_sensitive_info(args, str(val))
        show += f"  - {arg}: {val}\n"  # noqa: E221
    return show
