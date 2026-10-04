"""Reviewed portraits for named study contacts.

A portrait is attached only when a node matches the recorded person by email, or by the same registered
study and the same name — never by a name alone (a publication author "Barbour K" is not assumed to be
the study contact Kristen Barbour).
"""
import re

PEOPLE = [
    dict(name='Kayla R Cottiers', studies=['NCT07457736'], emails=['kayla.cottiers@yale.edu'],
         file='person-kayla-r-cottiers.jpg', note='Portrait supplied by the Asterisk team, 2026-10-04.'),
    dict(name='Kristen Barbour', studies=['NCT07847918'], emails=['kbarbour@scripps.edu'],
         file='person-kristen-barbour.jpg', note='Portrait supplied by the Asterisk team, 2026-10-04.'),
    dict(name='Shannan Henry', studies=['NCT07457736'], emails=['shannan.henry@yale.edu'],
         file='person-shannan-henry.jpg', note='Portrait supplied by the Asterisk team, 2026-10-04.'),
]
FILES = [p['file'] for p in PEOPLE]


def person_key(label):
    # "Kristen Barbour, MD" and "Kayla R. Cottiers" compare as "kristen barbour" / "kayla r cottiers".
    return ' '.join(re.sub(r'[^a-z ]', ' ', label.split(',')[0].lower()).split())


def portrait(node):
    if node.get('kind') != 'researcher':
        return None
    email = (node.get('email') or '').strip().lower()
    study = re.match(r'study-contact:(NCT\d+):', node.get('id', ''))
    for person in PEOPLE:
        if email and email in person['emails']:
            return person
        if study and study.group(1) in person['studies'] and person_key(node.get('label', '')) == person_key(person['name']):
            return person
    return None


def enrich_person(node):
    person = portrait(node)
    return {**node, 'image': '/lead-images/' + person['file'], 'image_note': person['note']} if person else node
