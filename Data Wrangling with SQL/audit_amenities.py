# Written for Python 3.7
# -*- coding: utf-8 -*-
import re
import xml.etree.ElementTree as ETree
from pprint import pprint as pp
from collections import defaultdict

osm_file = "columbus.osm"

# Regex pattern to find potential amenities name issues
amenities_type_re = re.compile(r"\S+(\s\S+)*", re.IGNORECASE)
amenities_type_name = defaultdict(set)
amenities_type_count = defaultdict(int)

# List of expected amenities in the dataset
expected_amenities_names = [
    "parking",
    "restaurant",
    "school",
    "fast_food",
    "bank",
    "library",
    "pharmacy",
    "clinic",
    "car_wash",
    "place_of_worship",
    "shelter",
    "theatre",
    "doctors",
    "dentist",
    "bar",
]


def audit_amenities_name(amenities_name):
    """ audit_amenities_name will audit for non-expected amenities names

    :param amenities_name: a name that needs to be audited
    :return: nothing, amenities_type_name & amenities_type_count are updated
    """
    reg_match = amenities_type_re.search(amenities_name)
    if reg_match:
        amenity = reg_match.group()
        if amenity not in expected_amenities_names:
            amenities_type_name[amenity].add(amenities_name)
            amenities_type_count[amenity] += 1


def is_amenities_name(element):
    """ is_amenities_name returns a boolean if attribute is 'addr:amenities'

    :param element: an element to be checked
    :return: True if attribute key is 'addr:amenities'
    """
    return element.attrib["k"] == "amenity"


def run_amenities_name_audit():
    """ Provides summary of amenities names along with counts

    :return: None
    """
    for event, element in ETree.iterparse(osm_file, events=("start",)):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_amenities_name(tag):
                    audit_amenities_name(tag.attrib["v"])
    pp(sorted(dict(amenities_type_count).items(), key=lambda kv: kv[1], reverse=True))
    # pp(amenities_type_name)


# Mapping used to consolidate classifications
amenity_mapping = {
    "university": "school",
    "college": "school",
    "kindergarten": "school",
    "bar;restaurant": "restaurant",
    "conference_centre": "community_center",
    "exhibition_centre": "community_center",
    "social_facility": "community_center",
    "public_building": "government_office",
    "post_office": "post_box",
}


def clean_amenities_name_values(name, mapping):
    """ clean_amenities_name_value corrects the name supplied with the correct name from mapping

    :param name: a amenities name that will be cleaned
    :param mappings: a mapping of bad values to good values
    :return: corrected amenities name
    """
    for amenity in mapping:
        if amenity in name:
            name = re.sub(r"\b" + re.escape(amenity), mapping[amenity], name)
    return name


if __name__ == "__main__":
    run_amenities_name_audit()
