# Written for Python 3.7
# -*- coding: utf-8 -*-7
import re
import xml.etree.ElementTree as ETree
from pprint import pprint as pp
from collections import defaultdict

osm_file = "columbus.osm"

# Regex pattern to find potential postal name issues
postal_code_re = re.compile(r"^(\d{5}|\d{5}-\d{4})$|\w.+", re.IGNORECASE)
postal_code_list = defaultdict(set)
postal_type_count = defaultdict(int)

# List of expected postal codes in the dataset
# http://www.mapszipcode.com/ohio/columbus/
expected_postal_names = [
    "43085",
    "43201",
    "43202",
    "43203",
    "43204",
    "43205",
    "43206",
    "43207",
    "43209",
    "43210",
    "43211",
    "43212",
    "43213",
    "43214",
    "43215",
    "43217",
    "43219",
    "43220",
    "43221",
    "43222",
    "43223",
    "43224",
    "43227",
    "43228",
    "43229",
    "43230",
    "43231",
    "43232",
    "43235",
    "43240",
]


def audit_postal_name(postal_name):
    """ audit_postal_name will audit for non-expected postal names

    :param postal_name: a name that needs to be audited
    :return: nothing, postal_type_name & postal_type_count are updated
    """
    reg_match = postal_code_re.search(postal_name)
    if reg_match:
        postal_names = reg_match.group()
        if postal_names not in expected_postal_names:
            postal_code_list[postal_names].add(postal_name)
            postal_type_count[postal_names] += 1


def is_postal_name(element):
    """ is_postal_name returns a boolean if attribute is 'addr:postal'

    :param element: an element to be checked
    :return: True if attribute key is 'addr:postal'
    """
    return element.attrib["k"] == "addr:postcode" or element.attrib["k"] == "addr:postal_code"


def run_postal_code_audit():
    """ Provides summary of postal names along with counts

    :return: None
    """
    for event, element in ETree.iterparse(osm_file, events=("start",)):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_postal_name(tag):
                    audit_postal_name(tag.attrib["v"])
    pp(sorted(dict(postal_type_count).items(), key=lambda kv: kv[1], reverse=True))


# mappings to clean erronous postal codes
postal_mapping = {
    "43328": "Invalid",
    "43029": "Invalid",
    "4313": "Invalid",
    "43220-4800": "43220",
    "43207-2431": "43207",
    "43215-1430": "43215",
    "East Livingston Av": "Invalid",
}


def clean_postal_name_values(name, mappings):
    """ clean_postal_name_value corrects the name supplied with the correct name from mapping

    :param name: a postal name that will be cleaned
    :param mappings: a mapping of bad values to good values
    :return: corrected postal name
    """
    for postal_code in mappings:
        if postal_code in name:
            # check if length is greater than 5, to determine how to clean value
            if len(name) >= 6:
                name = re.split("[:;-]", name)[0]
            name = re.sub(r"\b" + re.escape(postal_code), mappings[postal_code], name)
    return name


if __name__ == "__main__":
    run_postal_code_audit()
