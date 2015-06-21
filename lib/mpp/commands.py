from prettytable import PrettyTable
from mpp.cmdparser import CmdParser
from mpp.core import get_podcasts

parser = CmdParser()

def list_podcasts(*args):
    t = PrettyTable()
    t.field_names = ['ID', 'Title', 'Last Episode Date', 'Dld', 'Rdy', 'Total']
    podcasts = core.
    t.add_row([1, 'Science Magazine Podcast', '2015-06-11 18:59:00', 0, 0, 317])
    t.add_row([2, 'This American Life', '2015-06-08 00:00:00', 0, 0, 149])
    t.align = 'r'
    t.align['Title'] = 'l'
    print(t)
