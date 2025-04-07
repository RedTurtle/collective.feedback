import re


def looks_like_path(string):
    return bool(re.match(r"^(/|/[^\s<>:\"|?*]+.*)$", string))
