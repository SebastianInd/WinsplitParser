import statistics


def _compute_aggregated_split_times(results: list) -> dict:
    """
    Computes aggregated and sorted split times from a list of results.

    Args:
        results (list): A list of dictionaries, each containing information about a person's result.

    Returns:
        dict: A dictionary where the keys are split numbers and the values are lists of split times sorted in ascending order.
    """

    aggregated_split_times = {}

    for person in results:
        for split in person["splits"]:
            split_number = split["split_number"]
            split_time = split["split_time"]

            if split_time is None:
                continue
            aggregated_split_times.setdefault(split_number, []).append(split_time)

    for key in aggregated_split_times:
        aggregated_split_times[key].sort()

    return aggregated_split_times


def _add_reference_splits(data: dict) -> None:
    """
    Adds the best split times and reference split times to the data dictionary.

    Args:
        data (dict): A dictionary containing race results and other related information.

    Modifies:
        data (dict): Adds the 'best_split_times' and 'reference_split_times' keys to the dictionary.
    """
    aggregated_split_times = _compute_aggregated_split_times(data["results"])
    best_split_times = {}
    reference_split_times = {}

    for split_number, splits in aggregated_split_times.items():
        best_split_times[split_number] = splits[0]
        reference_split_times[split_number] = statistics.mean(splits[:5])

    data["best_split_times"] = best_split_times
    data["reference_split_times"] = reference_split_times


def _add_split_analysis(data: dict) -> None:
    """
    Adds split analysis information to each runner's splits.

    Args:
        data (dict): A dictionary containing race results and other related information.

    Modifies:
        data (dict): Updates the 'results' key with split analysis
    """
    for person in data["results"]:
        for split in person["splits"]:
            split_number = split["split_number"]
            split_time = split["split_time"]
            best_split_time = data["best_split_times"][split_number]

            if split_time is None:
                split_gap = None
                percentage_gap = None
            else:
                split_gap = split_time - best_split_time
                percentage_gap = (split_gap / best_split_time) * 100

            split["split_gap"] = split_gap
            split["percentage_gap"] = percentage_gap


def process_data(data: dict):
    """
    Processes the given data to extract split information and compute the best split times
    for each split leg. Updates the results with split analysis and sets the winning time.

    Args:
        data (dict): A dictionary containing race results and other related information.

    Modifies:
        data (dict): Updates the 'results' key with split analysis and adds the 'winning_time' key.
    """
    _add_reference_splits(data)
    _add_split_analysis(data)

    data["winning_time"] = data["results"][0]["total_time"]
