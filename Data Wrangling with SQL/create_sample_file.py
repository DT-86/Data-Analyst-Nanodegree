# Written for Python 3.7
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

num_elements = 100  # top elements to gather
osm_map_data = "columbus.osm"
sample_file = f"columbus-sample-top-{num_elements}.osm"


def get_element(map_data, tags=("node", "way", "relation")):
    """get_element yields the element if it is the right type of tag

    :param map_data: xml structured file that needs parsing
    :type map_data: file
    :param tags: the tag types we want to yield, defaults to ("node", "way", "relation")
    :type tags: tuple, optional
    :yields: xml element
    """
    context = iter(ET.iterparse(map_data, events=("start", "end")))
    _, root = next(context)
    for event, elem in context:
        if event == "end" and elem.tag in tags:
            yield elem
            root.clear()


with open(sample_file, "wb") as output:
    output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write(b"<osm>\n ")

    for i, element in enumerate(get_element(osm_map_data)):
        # Write every top level element to new sample file
        if i % num_elements == 0:
            output.write(ET.tostring(element, encoding="utf-8"))

    output.write(b"</osm>")
