def sanitize_filename(name):
    """
    Replaces characters that are invalid in Windows filenames with underscores.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name
