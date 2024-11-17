import xml.etree.ElementTree as ET


def _extract_event_data(root: ET.Element, namespace: dict) -> dict:
    """
    Extracts the event name, date, and class name from the XML content.

    Args:
        root (ET.Element): The root element of the XML tree.
        namespace (dict): A dictionary mapping XML namespace prefixes to URIs.

    Returns:
        dict: A dictionary containing the event name, class name, and date.
    """
    event = root.find(".//ns:Event", namespace)
    name = event.find(".//ns:Name", namespace).text
    date = event.find(".//ns:Date", namespace).text
    class_result = root.find(".//ns:ClassResult", namespace)
    class_name = class_result.find(".//ns:Name", namespace).text

    return {"name": name, "class": class_name, "date": date}


def _compute_split_information(person_result: ET.Element, namespace: dict) -> list:
    """
    Computes split information from an XML element representing a person's result.

    Args:
        person_result (ET.Element): The XML element containing the person's result data.
        namespace (dict): The namespace dictionary for XML parsing.

    Returns:
        list: A list of dictionaries, each containing:
            - "control_code" (str): The control code of the split.
            - "time" (int or None): The time recorded at the split, or None if missing.
            - "split_time" (int or None): The time difference from the previous split, or None if not applicable.
    """
    splits = []
    previous_time = 0
    split_elements = person_result.findall(".//ns:SplitTime", namespace)
    for split in split_elements:
        status = split.get("status", None)
        control_code = split.find("ns:ControlCode", namespace).text

        if status == "Missing":
            time = None
        else:
            time = int(split.find("ns:Time", namespace).text)

        if previous_time is not None and time is not None:
            split_time = time - previous_time
        else:
            split_time = None

        splits.append(
            {
                "control_code": control_code,
                "time": time,
                "split_time": split_time,
            }
        )
        previous_time = time

    return splits


def _extract_person_result(person_result: ET.Element, namespace: dict) -> dict:
    """
    Extracts information about a person's result from an XML element.

    Args:
        person_result (ET.Element): The XML element containing the person's result information.
        namespace (dict): The namespace dictionary for XML parsing.

    Returns:
        dict: A dictionary containing the extracted information with the following keys:
            - "name" (str): The person's full name in the format "GivenName FamilyName".
            - "club" (str): The name of the person's club.
            - "status" (str): The result position or status.
            - "position" (int or None): The position of the person in the result.
            - "total_time" (int): The total time of the result in seconds.
            - "splits" (list): The split information computed by the _compute_split_information function.
    """
    person_dict = {}

    name = person_result.find(".//ns:Name", namespace)
    family_name = name.find("ns:Family", namespace).text
    given_name = name.find("ns:Given", namespace).text
    person_dict["name"] = f"{given_name} {family_name}"

    organisation = person_result.find(".//ns:Organisation", namespace)
    club = organisation.find("ns:Name", namespace).text
    person_dict["club"] = club

    result = person_result.find(".//ns:Result", namespace)
    status = result.find(".//ns:Status", namespace).text
    person_dict["status"] = status
    if status == "OK":
        person_dict["position"] = int(result.find("ns:Position", namespace).text)
    else:
        person_dict["position"] = None
    person_dict["total_time"] = int(result.find(".//ns:Time", namespace).text)

    person_dict["splits"] = _compute_split_information(person_result, namespace)

    return person_dict


def _extract_result_list(root: ET.Element, namespace: dict) -> list:
    """
    Parses the XML content and converts it to a list, including information about all splits.
    The split time is calculated as the time minus the time at the previous split time entry.

    Args:
        root (ET.Element): The root element of the XML tree.
        namespace (dict): The namespace dictionary for XML parsing.

    Returns:
        list: A list of dictionaries, each containing information about a person's result.
    """
    result_list = []

    # Find all PersonResult entries
    for person_result in root.findall(".//ns:PersonResult", namespace):
        person_dict = _extract_person_result(person_result, namespace)
        result_list.append(person_dict)

    return result_list


def _compute_best_split_times(result_list: list) -> dict:
    """
    Finds the best split time for each control from the parsed results.
    """
    best_split_times = {}

    for person in result_list:
        for split in person["splits"]:
            control_code = split["control_code"]
            split_time = split["split_time"]

            if split_time is None:
                continue
            elif control_code not in best_split_times:
                best_split_times[control_code] = split_time
            elif split_time < best_split_times[control_code]:
                best_split_times[control_code] = split_time

    return best_split_times


def _add_split_analysis(result_list: list, best_split_times: dict) -> None:
    """
    Adds split analysis information to each runner's splits.
    """
    for person in result_list:
        for split in person["splits"]:
            control_code = split["control_code"]
            split_time = split["split_time"]
            best_split_time = best_split_times[control_code]

            if split_time is None:
                split_gap = None
                percentage_gap = None
            else:
                split_gap = split_time - best_split_time
                percentage_gap = (split_gap / best_split_time) * 100

            split["split_gap"] = split_gap
            split["percentage_gap"] = percentage_gap


def process_xml(xml_content: str) -> dict:
    """
    Processes the XML content to extract split information and compute the best split times
    for each control.
    """
    root = ET.fromstring(xml_content)
    namespace = {"ns": "http://www.orienteering.org/datastandard/3.0"}

    event_data = _extract_event_data(root, namespace)
    result_list = _extract_result_list(root, namespace)
    best_split_times = _compute_best_split_times(result_list)
    _add_split_analysis(result_list, best_split_times)

    return {
        "event_data": event_data,
        "results": result_list,
        "winning_time": result_list[0]["total_time"],
    }


# Example usage
if __name__ == "__main__":
    with open("sample.xml", "r") as file:
        xml_content = file.read()
    result = process_xml(xml_content)
    print(result)
