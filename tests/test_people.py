import unittest

from atlas.people import enrich_person, portrait


class PortraitTests(unittest.TestCase):
    def test_portrait_needs_study_and_name_or_email(self):
        contact = dict(kind='researcher', id='study-contact:NCT07847918:0', label='Kristen Barbour, MD')
        self.assertEqual(enrich_person(contact)['image'], '/lead-images/person-kristen-barbour.jpg')
        by_email = dict(kind='researcher', id='study-contact:NCT00000001:0', label='K. Cottiers', email='Kayla.Cottiers@yale.edu')
        self.assertEqual(portrait(by_email)['file'], 'person-kayla-r-cottiers.jpg')
        same_study = dict(kind='researcher', id='study-contact:NCT07457736:0', label='Shannan Henry')
        self.assertEqual(portrait(same_study)['file'], 'person-shannan-henry.jpg')

    def test_name_alone_never_attaches_a_photo(self):
        for node in (dict(kind='researcher', id='atlas:author:PMID:42447769:0', label='Barbour K'),
                     dict(kind='researcher', id='study-contact:NCT99999999:0', label='Kristen Barbour'),
                     dict(kind='institution', id='study-contact:NCT07847918:0', label='Kristen Barbour')):
            self.assertNotIn('image', enrich_person(node))
