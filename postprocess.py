import multiprocessing
import time
import logging

from pynab import log

import pynab.groups
import pynab.binaries
import pynab.releases
import pynab.tvrage
import pynab.rars
import pynab.nfos
import pynab.imdb

import scripts.quick_postprocess
import scripts.rename_bad_releases

import config

def mp_error(msg, *args):
    return multiprocessing.get_logger().error(msg, *args)


def process_tvrage(limit):
    pynab.tvrage.process()


def process_nfos(limit):
    pynab.nfos.process()


def process_rars(limit):
    pynab.rars.process()


def process_imdb(limit):
    pynab.imdb.process()


if __name__ == '__main__':
    log.info('Starting post-processing...')

    # print MP log as well
    multiprocessing.log_to_stderr().setLevel(logging.DEBUG)

    # start with a quick post-process
    log.info('Starting with a quick post-process to clear out the cruft that\'s available locally...')
    scripts.quick_postprocess.local_postprocess()

    while True:
        # grab and append tvrage data to tv releases
        tvrage_p = None
        if config.site['process_tvrage']:
            tvrage_p = multiprocessing.Process(target=process_tvrage, args=(config.site['tvrage_limit'],))
            tvrage_p.start()

        imdb_p = None
        if config.site['process_imdb']:
            imdb_p = multiprocessing.Process(target=process_imdb, args=(config.site['imdb_limit'],))
            imdb_p.start()

        # grab and append nfo data to all releases
        nfo_p = None
        if config.site['process_nfos']:
            nfo_p = multiprocessing.Process(target=process_nfos, args=(config.site['nfo_limit'],))
            nfo_p.start()

        # check for passwords, file count and size
        rar_p = None
        if config.site['process_rars']:
            rar_p = multiprocessing.Process(target=process_rars, args=(config.site['rar_limit'],))
            rar_p.start()

        if rar_p:
            rar_p.join()

        if imdb_p:
            imdb_p.join()

        if tvrage_p:
            tvrage_p.join()

        if nfo_p:
            nfo_p.join()

        # rename misc->other and all ebooks
        scripts.rename_bad_releases.rename_bad_releases(8010)
        scripts.rename_bad_releases.rename_bad_releases(7020)

        if config.site['delete_bad_releases']:
            log.info('Deleting bad releases...')
            # not confident in this yet
            #db.releases.remove({''})

        # wait for the configured amount of time between cycles
        log.info('Sleeping for {:d} seconds...'.format(config.site['postprocess_wait']))
        time.sleep(config.site['postprocess_wait'])