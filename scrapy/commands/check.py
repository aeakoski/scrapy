from __future__ import print_function
import time
import sys
from collections import defaultdict
from unittest import TextTestRunner, TextTestResult as _TextTestResult

from scrapy.commands import ScrapyCommand
from scrapy.contracts import ContractsManager
from scrapy.utils.misc import load_object
from scrapy.utils.conf import build_component_list


class TextTestResult(_TextTestResult):
    def printSummary(self, start, stop):
        write = self.stream.write
        writeln = self.stream.writeln

        run = self.testsRun
        plural = "s" if run != 1 else ""

        writeln(self.separator2)
        writeln("Ran %d contract%s in %.3fs" % (run, plural, stop - start))
        writeln()

        infos = []
        if not self.wasSuccessful():
            write("FAILED")
            failed, errored = map(len, (self.failures, self.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            write("OK")

        if infos:
            writeln(" (%s)" % (", ".join(infos),))
        else:
            write("\n")


class Command(ScrapyCommand):
    requires_project = True
    default_settings = {'LOG_ENABLED': False}

    def syntax(self):
        return "[options] <spider>"

    def short_desc(self):
        return "Check spider contracts"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-l", "--list", dest="list", action="store_true",
                          help="only list contracts, without checking them")
        parser.add_option("-v", "--verbose", dest="verbose", default=False, action='store_true',
                          help="print contract tests for all spiders")

    def run(self, args, opts):
        #Branch coverage
        f = open("/tmp/run","a")
        f.write("0000\n")

        # load contracts
        contracts = build_component_list(self.settings.getwithbase('SPIDER_CONTRACTS'))
        conman = ContractsManager(load_object(c) for c in contracts)
        runner = TextTestRunner(verbosity=2 if opts.verbose else 1)
        result = TextTestResult(runner.stream, runner.descriptions, runner.verbosity)

        # contract requests
        contract_reqs = defaultdict(list)

        spider_loader = self.crawler_process.spider_loader
        
        for spidername in args or spider_loader.list():

            f.write("0001\n")
            spidercls = spider_loader.load(spidername)
            spidercls.start_requests = lambda s: conman.from_spider(s, result)

            tested_methods = conman.tested_methods_from_spidercls(spidercls)
            if opts.list:
                f.write("0002\n")
                for method in tested_methods:
                    f.write("0003\n")
                    contract_reqs[spidercls.name].append(method)
            elif tested_methods:
                f.write("0004\n")
                self.crawler_process.crawl(spidercls)
            else:
                f.write("0005\n")

        # start checks
        if opts.list:
            f.write("0006\n")
            for spider, methods in sorted(contract_reqs.items()):
                f.write("0007\n")
                if not methods and not opts.verbose:
                    f.write("0008\n")
                    continue
                print(spider)
                for method in sorted(methods):
                    f.write("0009\n")
                    print('  * %s' % method)
        else:
            f.write("0010\n")
            start = time.time()
            self.crawler_process.start()
            stop = time.time()

            result.printErrors()
            result.printSummary(start, stop)
            self.exitcode = int(not result.wasSuccessful())

