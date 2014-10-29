# -*- coding: utf-8  -*-
"""Test Link functionality."""
#
# (C) Pywikipedia bot team, 2014
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'

import pywikibot
from pywikibot import config2 as config
from pywikibot.page import Link
from pywikibot.exceptions import Error, InvalidTitle
from tests.aspects import unittest, DefaultDrySiteTestCase, TestCase


# ---- Tests checking if the parser does (not) accept (in)valid titles


class TestLink(DefaultDrySiteTestCase):

    """
    Test parsing links with DrySite.

    The DrySite is using the builtin namespaces which behaviour is controlled
    in this repository so namespace aware tests do work, even when the actual
    default site is using completely different namespaces.
    """

    def test_valid(self):
        self.assertEqual(Link('Sandbox', self.get_site()).title, 'Sandbox')
        self.assertEqual(Link('A "B"', self.get_site()).title, 'A "B"')
        self.assertEqual(Link('A \'B\'', self.get_site()).title, 'A \'B\'')
        self.assertEqual(Link('.com', self.get_site()).title, '.com')
        self.assertEqual(Link('~', self.get_site()).title, '~')
        self.assertEqual(Link('"', self.get_site()).title, '"')
        self.assertEqual(Link('\'', self.get_site()).title, '\'')
        self.assertEqual(Link('Talk:Sandbox', self.get_site()).title, 'Sandbox')
        self.assertEqual(Link('Talk:Foo:Sandbox', self.get_site()).title, 'Foo:Sandbox')
        self.assertEqual(Link('File:Example.svg', self.get_site()).title, 'Example.svg')
        self.assertEqual(Link('File_talk:Example.svg', self.get_site()).title, 'Example.svg')
        self.assertEqual(Link('Foo/.../Sandbox', self.get_site()).title, 'Foo/.../Sandbox')
        self.assertEqual(Link('Sandbox/...', self.get_site()).title, 'Sandbox/...')
        self.assertEqual(Link('A~~', self.get_site()).title, 'A~~')
        self.assertEqual(Link(':A', self.get_site()).title, 'A')
        # Length is 256 total, but only title part matters
        self.assertEqual(Link('Category:' + 'X' * 248, self.get_site()).title, 'X' * 248)
        self.assertEqual(Link('X' * 252, self.get_site()).title, 'X' * 252)
        self.assertEqual(Link('A%20B', self.get_site()).title, 'A B')
        self.assertEqual(Link('A &eacute; B', self.get_site()).title, u'A é B')
        self.assertEqual(Link('A &#233; B', self.get_site()).title, u'A é B')
        self.assertEqual(Link('A &#x00E9; B', self.get_site()).title, u'A é B')

        l = Link('A | B', self.get_site())
        self.assertEqual(l.title, 'A')
        self.assertEqual(l.anchor, ' B')

        l = Link('A%23B', self.get_site())
        self.assertEqual(l.title, 'A')
        self.assertEqual(l.section, 'B')

    def test_invalid(self):
        self.assertRaises(InvalidTitle, Link('', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link(':', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('__  __', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('  __  ', self.get_site()).parse)
        # Bad characters forbidden regardless of wgLegalTitleChars
        self.assertRaises(InvalidTitle, Link('A [ B', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('A ] B', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('A { B', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('A } B', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('A < B', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('A > B', self.get_site()).parse)
        # URL encoding
        # %XX is understood by wikimedia but not %XXXX
        self.assertRaises(InvalidTitle, Link('A%2523B', self.get_site()).parse)
        # A link is invalid if their (non-)talk page would be in another
        # namespace than the link's "other" namespace
        self.assertRaises(InvalidTitle, Link('Talk:File:Example.svg', self.get_site()).parse)
        # Directory navigation
        self.assertRaises(InvalidTitle, Link('.', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('..', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('./Sandbox', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('../Sandbox', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('Foo/./Sandbox', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('Foo/../Sandbox', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('Sandbox/.', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('Sandbox/..', self.get_site()).parse)
        # Tilde
        self.assertRaises(InvalidTitle, Link('A ~~~ Name', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('A ~~~~ Signature', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('A ~~~~~ Timestamp', self.get_site()).parse)
        # Overlength
        self.assertRaises(InvalidTitle, Link('x' * 256, self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('Invalid:' + 'X' * 248, self.get_site()).parse)
        # Namespace prefix without actual title
        self.assertRaises(InvalidTitle, Link('Talk:', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('Category: ', self.get_site()).parse)
        self.assertRaises(InvalidTitle, Link('Category: #bar', self.get_site()).parse)


# ---- The first set of tests are explicit links, starting with a ':'.


class TestPartiallyQualifiedExplicitLinkSameSiteParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def setUp(self):
        self.old_lang = config.mylang
        self.old_family = config.family

    def tearDown(self):
        config.mylang = self.old_lang
        config.family = self.old_family

    def test_partially_qualified_NS0_code(self):
        """Test ':wikipedia:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 4)

    def test_partially_qualified_NS1_code(self):
        """Test ':wikipedia:Talk:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Talk:Main Page')
        self.assertEqual(link.namespace, 4)

    def test_partially_qualified_NS0_family(self):
        """Test ':en:Main Page' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_partially_qualified_NS1_family(self):
        """Test ':en:Talk:Main Page' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestPartiallyQualifiedExplicitLinkDifferentCodeParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def setUp(self):
        self.old_lang = config.mylang
        self.old_family = config.family

    def tearDown(self):
        config.mylang = self.old_lang
        config.family = self.old_family

    def test_partially_qualified_NS0_family(self):
        """Test ':en:Main Page' on dewp is namespace 0."""
        config.mylang = 'de'
        config.family = 'wikipedia'
        link = Link(':en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_partially_qualified_NS1_family(self):
        """Test ':en:Talk:Main Page' on dewp is namespace 1."""
        config.mylang = 'de'
        config.family = 'wikipedia'
        link = Link(':en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestPartiallyQualifiedExplicitLinkDifferentFamilyParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def setUp(self):
        self.old_lang = config.mylang
        self.old_family = config.family

    def tearDown(self):
        config.mylang = self.old_lang
        config.family = self.old_family

    def test_partially_qualified_NS0_code(self):
        """Test ':wikipedia:Main Page' on enws is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link(':wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_partially_qualified_NS1_code(self):
        """Test ':wikipedia:Talk:Main Page' on enws is ns 1."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link(':wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedSameNamespaceFamilyParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def test_namespace_vs_family(self):
        """Test namespace is selected before family."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':wikipedia:en:Main Page')
        link.parse()
        self.assertEqual(link.title, 'En:Main Page')
        self.assertEqual(link.namespace, 4)

        link = Link(':wikipedia:en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'En:Talk:Main Page')
        self.assertEqual(link.namespace, 4)


class TestFullyQualifiedExplicitLinkSameFamilyParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test ':en:wikipedia:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':en:wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 4)

    def test_fully_qualified_NS1_code(self):
        """Test ':en:wikipedia:Talk:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':en:wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Talk:Main Page')
        self.assertEqual(link.namespace, 4)


class TestFullyQualifiedExplicitLinkDifferentFamilyParser(TestCase):

    """Link tests."""

    sites = {
        'enws': {
            'family': 'wikisource',
            'code': 'en'
        },
        'enwp': {
            'family': 'wikipedia',
            'code': 'en'
        }
    }
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test ':en:wikipedia:Main Page' on enws is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link(':en:wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_code(self):
        """Test ':en:wikipedia:Main Page' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link(':en:wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)

    def test_fully_qualified_NS0_family(self):
        """Test ':wikipedia:en:Main Page' on enws is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link(':wikipedia:en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_family(self):
        """Test ':wikipedia:en:Talk:Main Page' on enws is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link(':wikipedia:en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedExplicitLinkNoLangConfigFamilyParser(TestCase):

    """Link tests."""

    sites = {
        'wikidata': {
            'family': 'wikidata',
            'code': 'wikidata'
        },
        'enwp': {
            'family': 'wikipedia',
            'code': 'en'
        }
    }
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test ':en:wikipedia:Main Page' on wikidata is namespace 4."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link(':en:wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 4)

    def test_fully_qualified_NS1_code(self):
        """Test ':en:wikipedia:Talk:Main Page' on wikidata is namespace 4."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link(':en:wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Talk:Main Page')
        self.assertEqual(link.namespace, 4)

    def test_fully_qualified_NS0_family(self):
        """Test ':wikipedia:en:Main Page' on wikidata is namespace 0."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link(':wikipedia:en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_family(self):
        """Test ':wikipedia:en:Talk:Main Page' on wikidata is namespace 1."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link(':wikipedia:en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedNoLangFamilyExplicitLinkParser(TestCase):

    """Link tests."""

    sites = {
        'wikidata': {
            'family': 'wikidata',
            'code': 'wikidata'
        },
        'enwp': {
            'family': 'wikipedia',
            'code': 'en'
        },
        'test.wp': {
            'family': 'wikipedia',
            'code': 'test'
        },
    }
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test ':testwiki:wikidata:Q6' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':testwiki:wikidata:Q6')
        link.parse()
        self.assertEqual(link.site, self.get_site('wikidata'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_code(self):
        """Test ':testwiki:wikidata:Talk:Q6' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':testwiki:wikidata:Talk:Q6')
        link.parse()
        self.assertEqual(link.site, self.get_site('wikidata'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 1)

    def test_fully_qualified_NS0_family(self):
        """Test ':wikidata:testwiki:Q6' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':wikidata:testwiki:Q6')
        link.parse()
        self.assertEqual(link.site, self.get_site('test.wp'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_family(self):
        """Test ':wikidata:testwiki:Talk:Q6' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':wikidata:testwiki:Talk:Q6')
        link.parse()
        self.assertEqual(link.site, self.get_site('test.wp'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedOneSiteFamilyExplicitLinkParser(TestCase):

    """Link tests."""

    family = 'species'
    code = 'species'
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test ':species:species:Main Page' on species is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':species:species:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_code(self):
        """Test ':species:species:Talk:Main Page' on species is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link(':species:species:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


# ---- Tests of a Link without colons, which shouldnt be interwikis, follow.


class TestPartiallyQualifiedImplicitLinkSameSiteParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def setUp(self):
        self.old_lang = config.mylang
        self.old_family = config.family

    def tearDown(self):
        config.mylang = self.old_lang
        config.family = self.old_family

    def test_partially_qualified_NS0_code(self):
        """Test 'wikipedia:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 4)

    def test_partially_qualified_NS1_code(self):
        """Test 'wikipedia:Talk:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Talk:Main Page')
        self.assertEqual(link.namespace, 4)

    def test_partially_qualified_NS0_family(self):
        """Test 'en:Main Page' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_partially_qualified_NS1_family(self):
        """Test 'en:Talk:Main Page' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestPartiallyQualifiedImplicitLinkDifferentCodeParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def setUp(self):
        self.old_lang = config.mylang
        self.old_family = config.family

    def tearDown(self):
        config.mylang = self.old_lang
        config.family = self.old_family

    def test_partially_qualified_NS0_family(self):
        """Test 'en:Main Page' on dewp  is namespace 0."""
        config.mylang = 'de'
        config.family = 'wikipedia'
        link = Link('en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_partially_qualified_NS1_family(self):
        """Test 'en:Talk:Main Page' on dewp is namespace 1."""
        config.mylang = 'de'
        config.family = 'wikipedia'
        link = Link('en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestPartiallyQualifiedImplicitLinkDifferentFamilyParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def setUp(self):
        self.old_lang = config.mylang
        self.old_family = config.family

    def tearDown(self):
        config.mylang = self.old_lang
        config.family = self.old_family

    def test_partially_qualified_NS0_code(self):
        """Test 'wikipedia:Main Page' on enws is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link('wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_partially_qualified_NS1_code(self):
        """Test 'wikipedia:Talk:Main Page' on enws is ns 1."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link('wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedImplicitLinkSameFamilyParser(TestCase):

    """Link tests."""

    family = 'wikipedia'
    code = 'en'
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test 'en:wikipedia:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('en:wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 4)

    def test_fully_qualified_NS1_code(self):
        """Test 'en:wikipedia:Talk:Main Page' on enwp is namespace 4."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('en:wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Talk:Main Page')
        self.assertEqual(link.namespace, 4)


class TestFullyQualifiedImplicitLinkDifferentFamilyParser(TestCase):

    """Link tests."""

    sites = {
        'enws': {
            'family': 'wikisource',
            'code': 'en'
        },
        'enwp': {
            'family': 'wikipedia',
            'code': 'en'
        }
    }
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test 'en:wikipedia:Main Page' on enws is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link('en:wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_code(self):
        """Test 'en:wikipedia:Main Page' on enws is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link('en:wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)

    def test_fully_qualified_NS0_family(self):
        """Test 'wikipedia:en:Main Page' on enws is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link('wikipedia:en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_family(self):
        """Test 'wikipedia:en:Talk:Main Page' on enws is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikisource'
        link = Link('wikipedia:en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedImplicitLinkNoLangConfigFamilyParser(TestCase):

    """Link tests."""

    sites = {
        'wikidata': {
            'family': 'wikidata',
            'code': 'wikidata'
        },
        'enwp': {
            'family': 'wikipedia',
            'code': 'en'
        }
    }
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test 'en:wikipedia:Main Page' on wikidata is namespace 4."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link('en:wikipedia:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 4)

    def test_fully_qualified_NS1_code(self):
        """Test 'en:wikipedia:Talk:Main Page' on wikidata is not namespace 1."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link('en:wikipedia:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Talk:Main Page')
        self.assertEqual(link.namespace, 4)

    def test_fully_qualified_NS0_family(self):
        """Test 'wikipedia:en:Main Page' on wikidata is namespace 0."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link('wikipedia:en:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.namespace, 0)
        self.assertEqual(link.title, 'Main Page')

    def test_fully_qualified_NS1_family(self):
        """Test 'wikipedia:en:Talk:Main Page' on wikidata is namespace 1."""
        config.mylang = 'wikidata'
        config.family = 'wikidata'
        link = Link('wikipedia:en:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site('enwp'))
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedNoLangFamilyImplicitLinkParser(TestCase):

    """Link tests."""

    family = 'wikidata'
    code = 'test'
    cached = True

    def test_fully_qualified_NS0_code(self):
        """Test 'testwiki:wikidata:Q6' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('testwiki:wikidata:Q6')
        link.parse()
        self.assertEqual(link.site, pywikibot.Site('wikidata', 'wikidata'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_code(self):
        """Test 'testwiki:wikidata:Talk:Q6' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('testwiki:wikidata:Talk:Q6')
        link.parse()
        self.assertEqual(link.site, pywikibot.Site('wikidata', 'wikidata'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 1)

    def test_fully_qualified_NS0_family(self):
        """Test 'wikidata:testwiki:Q6' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('wikidata:testwiki:Q6')
        link.parse()
        self.assertEqual(link.site, pywikibot.Site('test', 'wikipedia'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_family(self):
        """Test 'wikidata:testwiki:Talk:Q6' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('wikidata:testwiki:Talk:Q6')
        link.parse()
        self.assertEqual(link.site, pywikibot.Site('test', 'wikipedia'))
        self.assertEqual(link.title, 'Q6')
        self.assertEqual(link.namespace, 1)


class TestFullyQualifiedOneSiteFamilyImplicitLinkParser(TestCase):

    """Link tests."""

    family = 'species'
    code = 'species'
    cached = True

    def test_fully_qualified_NS0_family_code(self):
        """Test 'species:species:Main Page' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('species:species:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_family_code(self):
        """Test 'species:species:Talk:Main Page' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('species:species:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)

    def test_fully_qualified_NS0_code(self):
        """Test 'species:Main Page' on enwp is namespace 0."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('species:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 0)

    def test_fully_qualified_NS1_code(self):
        """Test 'species:Talk:Main Page' on enwp is namespace 1."""
        config.mylang = 'en'
        config.family = 'wikipedia'
        link = Link('species:Talk:Main Page')
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'Main Page')
        self.assertEqual(link.namespace, 1)


class TestEmptyTitle(TestCase):

    """Test links which contain no title."""

    family = 'wikipedia'
    code = 'en'

    def test_interwiki_mainpage(self):
        """Test that Link allow links without a title to the main page."""
        link = Link('en:', self.get_site())
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, '')
        self.assertEqual(link.namespace, 0)

    def test_interwiki_namespace_without_title(self):
        """Test that Link doesn't allow links without a title."""
        link = Link('en:Help:', self.get_site())
        self.assertRaisesRegex(
            InvalidTitle, "'en:Help:' has no title.", link.parse)

    def test_no_text(self):
        """Test that Link doesn't allow empty."""
        link = Link('', self.get_site())
        self.assertRaisesRegex(
            InvalidTitle, "The link does not contain a page title", link.parse)

    def test_namespace_lookalike(self):
        """Test that Link does only detect valid namespaces."""
        link = Link('CAT:', self.get_site())
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'CAT:')
        self.assertEqual(link.namespace, 0)

        link = Link('en:CAT:', self.get_site())
        link.parse()
        self.assertEqual(link.site, self.get_site())
        self.assertEqual(link.title, 'CAT:')
        self.assertEqual(link.namespace, 0)


class TestInvalidInterwikiLinks(TestCase):

    """Test links to non-wikis."""

    family = 'wikipedia'
    code = 'en'

    def test_non_wiki_prefix(self):
        """Test that Link fails if the interwiki prefix is not a wiki."""
        link = Link('bugzilla:1337')
        self.assertRaisesRegex(
            Error,
            'bugzilla:1337 is not a local page on wikipedia:en, and the '
            'interwiki prefix bugzilla is not supported by PyWikiBot!',
            link.parse)

    def test_other_wiki_prefix(self):
        """Test that Link fails if the interwiki prefix is a unknown family."""
        link = Link('bulba:this-will-never-work')
        self.assertRaisesRegex(
            Error,
            'bulba:this-will-never-work is not a local page on wikipedia:en, '
            'and the interwiki prefix bulba is not supported by PyWikiBot!',
            link.parse)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
