#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
from configuration import Configuration  # , ConfigurationException
from contextlib import contextmanager
from downloader import download_large_file, get_online_file
from environment import environment
from lxml import etree
from progressbar import ProgressBar
from system_utils import makedirs
from xml_utils import qualified_name
from wikimarkup import parse_wikimarkup
import errno
import bz2
import os


# project base directory
PROJECT_BASE = os.path.dirname(__file__)


class WikiCorpus(object):

    """Class representing corpus from Wikipedia of one language """

    # configuration file
    CORPUS_CONFIG_PATH = os.path.join(PROJECT_BASE, 'corpus-config.yaml')

    # original dump file name
    DUMP_ORIGINAL_NAME = 'pages-articles.xml.bz2'

    # dump url
    DUMP_URL_GENERAL = 'http://dumps.wikimedia.org/{lang}wiki/latest/'\
        + '{lang}wiki-latest-' + DUMP_ORIGINAL_NAME

    # md5 checksum file url
    MD5_URL_GENERAL = 'http://dumps.wikimedia.org/{lang}wiki/latest/'\
        + '{lang}wiki-latest-md5sums.txt'

    def __init__(self, language):
        """Initalization of WikiCorpus instance

        :language: unicode
        """
        # TODO: check if language is in dictionary of iso codes
        self._language = language

        ## TODO: logging
        #self._logfile = logfile

        # load configuration
        self._configuration = Configuration(WikiCorpus.CORPUS_CONFIG_PATH)

    # ------------------------------------------------------------------------
    # getters and setters
    # ------------------------------------------------------------------------

    def get_corpus_name(self):
        """ Returns corpus name
        """
        return self._configuration.get('corpus-name').format(
            lang=self.language())

    def get_dump_path(self):
        """ Returns path to dump
        """
        # full dumps are bzipped, while sample dumps are uncompressed
        if self.is_dump_compressed():
            ext = self._configuration.get('extensions', 'compressed-dump')
        else:
            ext = self._configuration.get('extensions', 'uncompressed-dump')

        # dump file name = corpus name + extension
        dump_file_name = '{name}.{ext}'.format(
            name=self.get_corpus_name(),
            ext=ext)

        # path = path to verticals + dump file name
        path = os.path.join(
            self.get_uncompiled_corpus_path(),
            dump_file_name)
        return path

    def get_prevertical_path(self):
        """ Returns path to prevertical
        """
        # prevertical file name = corpus name + extension
        prevertical_file_name = '{name}.{ext}'.format(
            name=self.get_corpus_name(),
            ext=self._configuration.get('extensions', 'prevertical'))

        # path = path to verticals + prevertical file name
        path = os.path.join(
            self.get_uncompiled_corpus_path(),
            prevertical_file_name)
        return path

    def get_vertical_path(self):
        """ Returns path to vertical
        """
        # vertical file name = corpus name + extension
        vertical_file_name = '{name}.{ext}'.format(
            name=self.get_corpus_name(),
            ext=self._configuration.get('extensions', 'vertical'))

        # path = path to verticals + vertical file name
        path = os.path.join(
            self.get_uncompiled_corpus_path(),
            vertical_file_name)
        return path

    def get_uncompiled_corpus_path(self):
        """ Returns path to directory with verticals for this corpus

        It will also creates non-existing directories on this path
        """
        path = os.path.join(
            environment.verticals_path(),
            self.get_corpus_name())
        makedirs(path)
        return path

    def get_compiled_corpus_path(self):
        """ Returns path to directory with compiled corpus

        It will also creates non-existing directories on this path
        """
        path = os.path.join(
            environment.compiled_corpora_path(),
            self.get_corpus_name())
        makedirs(path)
        return path

    #def is_sample(self):
    #    """ Returns True if this is a sample corpus
    #    """
    #    return bool(self.sample_size())

    def is_dump_compressed(self):
        """Returns True if dumps is compress, False otherwise.
        """
        # dumps for full languages are always compressed
        return True

    def language(self):
        """ Returns corpus language
        """
        return self._language

    # ------------------------------------------------------------------------
    #  corpus building methods
    # ------------------------------------------------------------------------

    def download_dump(self, force=False):
        """ Downloads dump of Wikipedia

        :force: Boolean
            if True, it downloads dump even if some dump with
            target name is already downloaded
        """
        # select dump path
        dump_path = self.get_dump_path()
        if os.path.exists(dump_path) and not force:
            # TODO: use logging instead of prins (everywhere)
            print 'Dump {name} already exists.'.format(name=dump_path)
            return

        # select dump url
        dump_url = WikiCorpus.DUMP_URL_GENERAL.format(lang=self.language())

        # TODO: logging
        print 'Started downloading {iso}-wiki dump\nfrom: {url}\ninto: {path}'\
            .format(iso=self.language(), url=dump_url, path=dump_path)

        # find MD5 checksum
        md5_url = WikiCorpus.MD5_URL_GENERAL.format(lang=self.language())
        md5sums = get_online_file(md5_url, lines=True)
        for file_md5, file_name in map(lambda x: x.split(), md5sums):
            if file_name.endswith(WikiCorpus.DUMP_ORIGINAL_NAME):
                md5sum = file_md5
                break
        else:
            # TODO logging
            print 'no matching MD5 checksum for the dump found'
            md5sum = None

        # downloading
        download_large_file(dump_url, dump_path, md5sum=md5sum)

        # TODO: logging
        print 'Downloading of {lang}-wiki dump finished'.format(
            lang=self.language(),
            path=dump_path)

    def create_prevertical(self):
        """ Parses dump (outer XML, inner Wiki Markup) and creates prevertical
        """
        prevertical_path = self.get_prevertical_path()

        # find the namespace
        # TODO: vyfaktorovat do nejake funkce / metody
        #   -> dump by mela byt vlastni trida (metody open, len, get_namespace
        with self._open_dump() as dump_file:
            # read first event, which is ('start', root element),
            context_for_ns = etree.iterparse(dump_file, events=('start',))
            _, root = context_for_ns.next()
            # get namespace information from the root element,
            # None means implicit namespace (without prefix)
            namespace = root.nsmap[None]
            del context_for_ns

        # create qualified names (= names with namespaces) for tags we need
        TEXT_TAG = qualified_name('text', namespace)
        TITLE_TAG = qualified_name('title', namespace)
        REDIRECT_TAG = qualified_name('redirect', namespace)

        # iterate through xml and build a sample file
        with open(prevertical_path, 'w') as prevertical_file:
            with self._open_dump() as dump_file:
                context = etree.iterparse(dump_file, events=('end',))

                # find total dump size and create progress bar
                total_size = os.path.getsize(self.get_dump_path())
                progressbar = ProgressBar(total_size)

                pages = 0
                last_title = None
                # skip first page in full (copressed) dump since it's Main Page
                skip = 1 if self.is_dump_compressed() else 0

                # TODO: mely by se zapisovat i top level tag?
                #  (neco jako <wiki lang="en" sample-size="10">) ???

                # iterate through end-events
                for event, elem in context:
                    # NOTE: this relies on the fact that <redirect> goes always
                    # before <text> (TODO: verify this has to be the case)
                    if elem.tag == REDIRECT_TAG:
                        # ignore redirect pages
                        skip += 1
                    elif elem.tag == TITLE_TAG:
                        # remember the title
                        last_title = elem.text
                    elif elem.tag == TEXT_TAG:
                        pages += 1  # TODO? pocitat projite / zpracovane ?
                        if skip > 0:
                            skip -= 1
                            continue
                        parsed_doc = parse_wikimarkup(elem.text, last_title)\
                            + '\n'
                        prevertical_file.write(parsed_doc.encode('utf-8'))
                        # approximate work done by position in dump file
                        progressbar.update(dump_file.tell())

                    # cleanup
                    elem.clear()
                    #while elem.getprevious() is not None:
                    #    del elem.getparent()[0]
                    for ancestor in elem.xpath('ancestor-or-self::*'):
                        while ancestor.getprevious() is not None:
                            del ancestor.getparent()[0]
                    if pages >= 1000:
                        break
                del context
        progressbar.finish()

        # log info (TODO: logging)
        print 'Prevertical of {name} created at:\n  {path}'.format(
            name=self.get_corpus_name(), path=prevertical_path)

    def tokenize_prevertical(self):
        """ Performes tokenization of prevertical
        """
        prevertical_path = self.get_prevertical_path()
        vertical_path = self.get_vertical_path()
        print prevertical_path, '->', vertical_path
        #raise NotImplementedError

    def morfologize_vertical(self, add_tags=True, add_lemmas=True):
        """ Adds morfological tag and/or lemma for each token in the vertical
        """
        vertical_path = self.get_vertical_path()
        print '<->', vertical_path
        #raise NotImplementedError

    def infere_terms_occurences(self):
        """ Labels all occurences of terms in morfolgized vertical
        """
        vertical_path = self.get_vertical_path()
        print '<->', vertical_path
        #raise NotImplementedError

    def compile_corpus(self):
        """ Compiles given corpora
        """
        # Creates configuration file, if it hasn't existed already
        vertical_path = self.get_vertical_path()
        compiled_corpus_path = self.get_compiled_corpus_path()
        print vertical_path, '->', compiled_corpus_path
        #raise NotImplementedError

    # ------------------------------------------------------------------------
    #
    # ------------------------------------------------------------------------

    def print_info(self):
        """ Returns corpus summary
        """
        print 'corpus name:', self.get_corpus_name()
        #raise NotImplementedError

    # ------------------------------------------------------------------------
    #  private methods
    # ------------------------------------------------------------------------

    @contextmanager
    def _open_dump(self):
        """Opened dump (prepared for reading) with statement manager

        Allows to write:
            with self._open_dump() as dump_file:
                do something
        And dump will be closed automatically no matter what.
        """
        dump_path = self.get_dump_path()
        try:
            # open dump
            if self.is_dump_compressed():
                dump_file = bz2.BZ2File(dump_path, 'r')
            else:
                dump_file = open(dump_path)
            yield dump_file
            # [after yield, the body of with statement will be executed]
        except IOError as exc:
            # errno.ENOENT = "No such file or directory"
            if exc.errno == errno.ENOENT:
                raise CorpusException('Dump file {name} doesn\'t exist.'
                    .format(name=dump_path))
        finally:
            # close dump
            dump_file.close()

    # ------------------------------------------------------------------------
    #  magic methods
    # ------------------------------------------------------------------------

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return 'WikiCorpus({lang})'.format(lang=self.language())

    def __unicode__(self):
        return repr(self)


# ---------------------------------------------------------------------------
#  Exceptions
# ---------------------------------------------------------------------------

class CorpusException(Exception):
    """ Class for reprezentation of exception raised during building corpus
    """
    pass
