#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Based on https://gist.github.com/pklaus/1029870

import json
import objc
import AddressBook as ab

import traceback
import pprint as pp

DEBUG = False
GROUP_NAME = "Christmas Cards"

def pythonize(objc_obj):
    if isinstance(objc_obj, objc.pyobjc_unicode):
        return unicode(objc_obj)
    elif isinstance(objc_obj, ab.NSDate):
        return objc_obj.description()
    elif isinstance(objc_obj, ab.NSCFDictionary) or isinstance(objc_obj, ab.__NSDictionaryM):
        # implicitly assuming keys are strings...
        return {k.lower(): pythonize(objc_obj[k])
                for k in objc_obj.keys()}
    elif isinstance(objc_obj, ab.ABMultiValueCoreDataWrapper):
        return [pythonize(objc_obj.valueAtIndex_(index))
                for index in range(0, objc_obj.count())]
    elif DEBUG:
        print objc_obj.__class__
        pp.pprint(objc_obj)

_default_skip_properties = frozenset(("com.apple.ABPersonMeProperty",
                                      "com.apple.ABImageData"))
def ab_person_to_dict(person, skip=None):
    skip = _default_skip_properties if skip is None else frozenset(skip)
    props = person.allProperties()
    return {prop.lower(): pythonize(person.valueForProperty_(prop))
            for prop in props if prop not in skip}

def group_named(group_name=GROUP_NAME):
    address_book = ab.ABAddressBook.sharedAddressBook()
    groups = address_book.groups()
    for group in groups:
        if group.valueForProperty_("GroupName") == group_name:
            return group

def address_book_group_people(group_name=GROUP_NAME):
    """
    Read the current user's AddressBook database, converting each person
    in the address book into a Dictionary of values. Some values (addresses,
    phone numbers, email, etc) can have multiple values, in which case a
    list of all of those values is stored. The result of this method is
    a List of Dictionaries, with each person represented by a single record
    in the list.
    Function adapted from: https://gist.github.com/pklaus/1029870
    """
    group = group_named(group_name)

    for person in group.members():
        if DEBUG:
            try:
                pp.pprint(person)
            except:
                traceback.print_exc()
        yield ab_person_to_dict(person)

def label_values(people):
    for person in people:
        name = "{first} {last}".format(**person)
        if 'address' in person:
            addresses = person['address']
        else:
            addresses = []
        yield name, addresses

if __name__ == '__main__':
    ENTRIES = []
    NEED_ADDRESS_PEOPLE = []
    CHECK_ADDRESS_PEOPLE = []

    for name, addresses in label_values(address_book_group_people(GROUP_NAME)):
        if len(addresses) == 0:
            NEED_ADDRESS_PEOPLE.append(name)
        elif len(addresses) > 1:
            CHECK_ADDRESS_PEOPLE.append(name)

        addr_strings = []
        for addr in addresses:
            try:
                addr_strings.append("{street}\n{city}, {state} {zip}".format(**addr))
            except KeyError:
                traceback.print_exc()
                pp.pprint(addr)

        ENTRIES.append(dict(name=name, addresses=addr_strings))

    with open('people.json', 'w') as outfile:
        json.dump(ENTRIES, outfile, indent=4)

    for name in CHECK_ADDRESS_PEOPLE:
        print "WARNING: Multiple addresses for {}".format(name)

    for name in NEED_ADDRESS_PEOPLE:
        print "WARNING: need address for {}".format(name)

