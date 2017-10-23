import argparse
import logging

from salamanca import data
from salamanca import currency

COMMANDS = {}

#
# Download wb data
#


def download_wb_cli(parser):
    inds = 'Indicators to Download'
    parser.add_argument('--ind', help=inds, nargs='+', default=None)
    log = 'Print log output during download.'
    parser.add_argument('--log', help=log, action="store_true")
    overwrite = 'Overwrite local files if they exist.'
    parser.add_argument('--overwrite', help=overwrite, action="store_true")


def download_wb(inds=None, log=False, overwrite=False, **kwargs):
    if log:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    wb = data.WorldBank()
    wb.iso_metadata(overwrite=overwrite)
    inds = inds or data.INDICATORS_WB
    for ind in inds:
        wb.query(ind, overwrite=overwrite)


COMMANDS['download_wb'] = (
    """Download national World Bank data to your machine""",
    download_wb_cli,
    download_wb,
)


#
# Currency Exchange
#

def exchange_cli(parser):
    amt = 'quantity of currency (default: 1.0)'
    parser.add_argument('-x', '--amt', help=amt, default=1.0)
    units = "units in which to do conversion [MER or PPP] (default: MER)"
    parser.add_argument('-u', '--units', help=units, default='MER')
    meth = "method to use to do conversion [deflator or cpi] (default: deflator)"
    parser.add_argument('-m', '--meth', help=meth, default='deflator')

    required = parser.add_argument_group('required arguments')
    _from = """
    ISO: 3-letter ISO code for the origin country, YEAR: origin year
    """
    required.add_argument('-f', '--from', help=_from,
                          nargs=2, metavar=('ISO', 'YEAR'), required=True)
    _to = """
    ISO: 3-letter ISO code for the destination country, YEAR: destination year
    """
    required.add_argument('-t', '--to', help=_to,
                          nargs=2, metavar=('ISO', 'YEAR'), required=True)


def exchange(**kwargs):
    amt = kwargs['amt']
    fromiso, fromyr = kwargs['from']
    toiso, toyr = kwargs['to']
    units = kwargs['units']
    inflation_method = kwargs['meth']

    xlator = currency.Translator()
    ret = xlator.exchange(amt,
                          fromiso=fromiso, fromyr=fromyr,
                          toiso=toiso, toyr=toyr,
                          units=units, inflation_method=inflation_method)
    print(ret)
    return ret


COMMANDS['exchange'] = (
    """Exchange currency from one country/year to another.""",
    exchange_cli,
    exchange,
)


def to_ppp_cli(parser):
    amt = 'quantity of currency in MER (default: 1.0)'
    parser.add_argument('-x', '--amt', help=amt, type=float, default=1.0)
    iso = '3-letter ISO code for the country'
    parser.add_argument('--iso', help=iso)
    year = 'year of conversion'
    parser.add_argument('--year', type=int, help=year)


def to_ppp(**kwargs):
    amt = kwargs['amt']
    iso = kwargs['iso']
    year = kwargs['year']

    xlator = currency.Translator()
    ret = amt * xlator.mer_to_ppp(iso, year)
    print(ret)
    return ret


COMMANDS['to_ppp'] = (
    """Exchange currency in MER to PPP.""",
    to_ppp_cli,
    to_ppp,
)


def to_mer_cli(parser):
    amt = 'quantity of currency in PPP (default: 1.0)'
    parser.add_argument('-x', '--amt', help=amt, type=float, default=1.0)
    iso = '3-letter ISO code for the country'
    parser.add_argument('--iso', help=iso)
    year = 'year of conversion'
    parser.add_argument('--year', type=int, help=year)


def to_mer(**kwargs):
    amt = kwargs['amt']
    iso = kwargs['iso']
    year = int(kwargs['year'])

    xlator = currency.Translator()
    ret = amt / xlator.mer_to_ppp(iso, year)
    print(ret)
    return ret


COMMANDS['to_mer'] = (
    """Exchange currency in PPP to MER.""",
    to_mer_cli,
    to_mer,
)


def main():
    descr = """
    Main CLI for salamanca.
    """
    parser = argparse.ArgumentParser(
        description=descr,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command')

    for cmd in COMMANDS:
        cli_help = COMMANDS[cmd][0]
        cli_func = COMMANDS[cmd][1]
        subparser = subparsers.add_parser(
            cmd,
            help=cli_help,
        )
        cli_func(subparser)

    args = parser.parse_args()
    cmd = args.command
    cmd_func = COMMANDS[cmd][2]
    cmd_func(**vars(args))


if __name__ == '__main__':
    main()
