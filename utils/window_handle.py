import pygetwindow as gw


def get_runelite_handle():
    """
    Fetches the handle of the first RuneLite window found.

    Returns:
    int: The handle of the RuneLite window, or None if not found.
    """
    windows = gw.getAllWindows()
    runelite_windows = [window for window in windows if "RuneLite" in window.title]

    if runelite_windows:
        return runelite_windows[0]._hWnd
    else:
        print("No RuneLite window found.")
        return None


def list_runelite_windows():
    """
    Lists all RuneLite windows with their handles and names.

    Returns:
    list: A list of tuples containing (handle, window_name) for each RuneLite window.
    """
    windows = gw.getAllWindows()
    runelite_windows = [window for window in windows if "RuneLite" in window.title]

    window_info = []

    for window in runelite_windows:
        handle = window._hWnd
        title = window.title
        window_name = title.split(' -')[0]  # Extract window name
        print(f"Handle: {handle}, Window Name: {window_name}")
        window_info.append((handle, window_name))

    return window_info


if __name__ == "__main__":
    # Example usage
    handle = get_runelite_handle()
    if handle:
        print(f"RuneLite window handle: {handle}")

    print("\nListing all RuneLite windows:")
    window_info = list_runelite_windows()
    for handle, window_name in window_info:
        print(f"Returned Handle: {handle}, Window Name: {window_name}")