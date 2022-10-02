def get_file(filename, mode="r"):
    if isinstance(filename, str):
        return open(filename, mode)
    return filename


def close_file(filename, f):
    """Close the file if filename is a string."""
    if hasattr(f, "close") and isinstance(filename, str):
        f.close()
