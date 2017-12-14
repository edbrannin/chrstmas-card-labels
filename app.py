#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Based on https://gist.github.com/pklaus/1029870

import objc
import AddressBook as ab

import pprint as pp

GROUP_NAME = "Christmas 2017"

def pythonize(objc_obj):
    if isinstance(objc_obj, objc.pyobjc_unicode):
        return unicode(objc_obj)
    elif isinstance(objc_obj, ab.NSDate):
        return objc_obj.description()
    elif isinstance(objc_obj, ab.NSCFDictionary):
        # implicitly assuming keys are strings...
        return {k.lower(): pythonize(objc_obj[k])
                for k in objc_obj.keys()}
    elif isinstance(objc_obj, ab.ABMultiValueCoreDataWrapper):
        return [pythonize(objc_obj.valueAtIndex_(index))
                for index in range(0, objc_obj.count())]


_default_skip_properties = frozenset(("com.apple.ABPersonMeProperty",
                                      "com.apple.ABImageData"))
def ab_person_to_dict(person, skip=None):
    skip = _default_skip_properties if skip is None else frozenset(skip)
    props = person.allProperties()
    return {prop.lower(): pythonize(person.valueForProperty_(prop))
            for prop in props if prop not in skip}

def address_book_group_to_list(group_name=GROUP_NAME):
    """
    Read the current user's AddressBook database, converting each person
    in the address book into a Dictionary of values. Some values (addresses,
    phone numbers, email, etc) can have multiple values, in which case a
    list of all of those values is stored. The result of this method is
    a List of Dictionaries, with each person represented by a single record
    in the list.
    Function adapted from: https://gist.github.com/pklaus/1029870
    """
    address_book = ab.ABAddressBook.sharedAddressBook()
    groups = address_book.groups()
    for group in groups:
        if group.valueForProperty_("GroupName") == group_name:
            break
    pp.pprint(dir(group.members.selector))
    pp.pprint(group.members.selector)
    return
    for person in group.members.selector:
        pp.pprint(person)
        yield ab_person_to_dict(person)
    pp.pprint(group.members)
    # people = address_book.people()
    # return [ab_person_to_dict(person) for person in people]

if __name__ == '__main__':
    for person in address_book_group_to_list():
        pp.pprint(person)
