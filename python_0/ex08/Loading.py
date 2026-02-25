import os


def ft_tqdm(lst: range):
    """Yield items from lst while displaying a progress bar."""
    total = len(lst)

    if total == 0:
        return
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80

    for index, item in enumerate(lst, start=1):

        percent = int(index / total * 100)
        prefix = f"{percent:3d}%|"
        suffix = f"| {index}/{total}"

        bar_space = term_width - len(prefix) - len(suffix) - 1
        bar_space = max(10, bar_space)

        filled = int(bar_space * index / total)
        if filled >= bar_space:
            bar = "█" * bar_space
        else:
            bar = "█" * filled + ">" + " " * (bar_space - filled - 1)

        print(f"\r{prefix}{bar}{suffix}", end="", flush=True)
        yield item

    print()
