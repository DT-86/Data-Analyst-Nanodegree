# Written for Python 3.7
# -*- coding: utf-8 -*-7
import re
import xml.etree.ElementTree as ETree
from pprint import pprint as pp
from collections import defaultdict

osm_file = "columbus.osm"

# Regex pattern to find potential street name issues
street_type_re = re.compile(r"\b\S+\.?$", re.IGNORECASE)
street_type_name = defaultdict(set)
street_type_count = defaultdict(int)

# List of expected street names in the dataset
expected_street_names = [
    "Avenue",
    "Boulevard",
    "Court",
    "Drive",
    "Lane",
    "Place",
    "Road",
    "Street",
]


def audit_street_name(street_name):
    """ audit_street_name will audit for non-expected street names

    :param street_name: a name that needs to be audited
    :return: nothing, street_type_name & street_type_count are updated
    """
    reg_match = street_type_re.search(street_name)
    if reg_match:
        street_names = reg_match.group()
        if street_names not in expected_street_names:
            street_type_name[street_names].add(street_name)
            street_type_count[street_names] += 1


def is_street_name(element):
    """ is_street_name returns a boolean if attribute is 'addr:street'

    :param element: an element to be checked
    :return: True if attribute key is 'addr:street'
    """
    return element.attrib["k"] == "addr:street"


def run_street_name_audit():
    """ Provides summary of street names along with counts

    :return: None
    """
    for event, element in ETree.iterparse(osm_file, events=("start",)):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_name(tag.attrib["v"])
    pp(sorted(dict(street_type_count).items(), key=lambda kv: kv[1], reverse=True))
    pp(street_type_name)


# Mapping used to correct abbreviated street names to a full names
street_mapping = {"St": "Street", "Dr": "Drive", "Dr.": "Drive", "Rd": "Road", "Ave": "Avenue"}


def clean_street_name_values(name, mappings):
    """ clean_street_name_value corrects the name supplied with the correct name from mapping

    :param name: a street name that will be cleaned
    :param mappings: a mapping of bad values to good values
    :return: corrected street name
    """
    new_street_name = name.title()
    for street_name in mappings:
        if street_name in new_street_name:
            new_street_name = re.sub(
                r"\b" + re.escape(street_name) + r"$", mappings[street_name], new_street_name
            )
    return new_street_name


if __name__ == "__main__":
    run_street_name_audit()
