import re


def _format_time(total_time_seconds: int) -> str:
    """
    Converts total time from seconds to mm:ss format.
    """
    if total_time_seconds is None:
        return "--"
    minutes, seconds = divmod(total_time_seconds, 60)
    return f"{minutes}.{int(seconds):02}"


def _format_runner_title(result: dict, winning_time: int) -> str:
    """
    Formats a single runner's result into a string with position, name, club, and total time.
    """
    position = result["position"]
    name = result["name"]
    club = result["club"]
    total_time = _format_time(result["total_time"])

    title = ""
    if position is not None:
        title += f"{position:>3}. "
    else:
        title += " --  "

    time_behind = _format_time(result["total_time"] - winning_time)
    title += f"{name[:20]:20} {'('+ club[:23]+ ')':25} {total_time:>6}"
    if position is not None and position > 1:
        title += f" (+{time_behind})"
    elif position is None:
        title += f" ({result['status']})"
    return title


def _format_runner_splits(splits: list, nr_of_elements_per_row: int) -> str:
    """
    Formats a single runner's splits.
    """
    lines = []

    for i in range(0, len(splits), nr_of_elements_per_row):
        total_times = []
        split_times = []
        split_gap_times = []
        split_gap_percentages = []

        for j, split in enumerate(splits[i : i + nr_of_elements_per_row]):
            total_times.append(f"{i + j + 1:>2}. {_format_time(split['time']):>6}")
            split_times.append(
                f"{split['control_code']:>3} {_format_time(split['split_time']):>6}"
            )
            split_gap = split.get("split_gap")
            split_gap_percentage = split.get("percentage_gap")
            if split_gap is not None:
                split_gap_times.append(f"{'+' + _format_time(split_gap):>10}")
                split_gap_percentages.append(
                    f"{'(+' + str(int(split_gap_percentage)) + '%)':>10}"
                )
            else:
                split_gap_times.append(f"{'':>10}")
                split_gap_percentages.append(f"{'':>10}")
        lines.append(" ".join(total_times))
        lines.append(" ".join(split_times))
        lines.append(" ".join(split_gap_times))
        lines.append(" ".join(split_gap_percentages))
        lines.append("")

    return "\n".join(lines)


def format_results(
    data: dict, basic_analysis: list, advanced_analysis: list, splits_per_row: int
) -> str:
    """
    Formats the results into a string with event data, runner titles, and optionally detailed splits.
    Each runner's result includes position, name, club, total time, and time behind the winner if applicable.

    Args:
        data (dict): The result data from parse_xml.
        basic_analysis (list): List of runner names for basic analysis.
        advanced_analysis (list): List of runner names for advanced analysis.
        splits_per_row (int): Number of split times to display per row.

    Returns:
        str: The formatted result string.
    """
    lines = []

    for result in data["results"]:
        if result["name"] in basic_analysis + advanced_analysis:
            lines.append(_format_runner_title(result, data["winning_time"]))
        if result["name"] in advanced_analysis:
            lines.append(_format_runner_splits(result["splits"], splits_per_row))

    return "\n".join(lines)


def get_file_title(event_data: dict) -> str:
    """
    Formats the event data into a string with the event name and date.
    """

    def _sanitize_filename(filename: str, max_length: int = 200) -> str:
        # Remove ASCII control characters
        filename = "".join(ch for ch in filename if ord(ch) >= 32)
        # Replace characters invalid on Windows filesystems with an underscore
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Collapse whitespace and strip ends
        filename = re.sub(r"\s+", " ", filename).strip()
        # Filenames can't end with a space or dot on Windows
        filename = filename.rstrip(" .")
        # Truncate if too long
        if len(filename) > max_length:
            filename = filename[:max_length].rstrip()
        return filename

    name = event_data.get("name", "event")
    date = event_data.get("date", "").replace("-", "")[2:]
    safe_name = _sanitize_filename(name)
    if not safe_name:
        safe_name = "event"
    # Ensure we don't produce leading/trailing whitespace in the final filename
    return f"{date} {safe_name}.docx".strip()


def format_event_data(event_data: dict) -> str:
    """
    Formats the event data into a string with the event name and date.
    """
    name = event_data["name"]
    class_name = event_data["class"]
    date = event_data["date"]
    return f"{name} - {class_name} ({date})"


# Example usage
if __name__ == "__main__":
    from src.parse_xml import parse_xml
    from src.process_data import process_data

    with open("sample.xml", "r", encoding="utf-8") as file:
        xml_content = file.read()
    basic_analysis = ["Vegard Kittilsen", "Filip Ossianson"]
    advanced_analysis = ["Sebastian Inderst"]
    data = parse_xml(xml_content)
    process_data(data)
    formatted_event = format_event_data(data["event_data"])
    formatted_results = format_results(
        data, basic_analysis, advanced_analysis, splits_per_row=7
    )
    print(formatted_event + "\n####################\n" + formatted_results)
