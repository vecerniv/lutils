from pathlib import Path


def get_latest_time(
    case_path: Path
) -> int:

    """
    Placeholder
    """

    times = []

    for dir in case_path.iterdir():
        try:
            time = int(dir.name)
        except:
            continue

        times.append(time)

    return max(times)
