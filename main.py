
import json
import re
import copy
import urllib
import datetime
import argparse

import arrow
import camelot

from ics import Calendar, Event
from zoom import *


DEBUG = True


TIME_ZONE = 'America/Lima'

def main(ifile, start_date, zoom_user=None):

    tables = camelot.read_pdf(ifile, pages='all')

    t_rot = json.loads(tables[0].df.to_json())
    t_blau = json.loads(tables[1].df.to_json())
    t_hh = json.loads(tables[2].df.to_json())
    t_muttersprache = json.loads(tables[3].df.to_json())

    if len(tables) > 6:
        t_turnen = json.loads(tables[4].df.to_json())
    else:
        t_turnen = None



    h_clases_rot = parse_times(t_rot)
    h_clases_blau = parse_times(t_blau)
    h_clases_hh = parse_times(t_hh)


    if t_turnen:
        clases_turnen = parse_time_turnen(t_turnen)


    week_rot = parse_week(t_rot, h_clases_rot)
    week_blau = parse_week(t_blau, h_clases_rot)
    week_hh = parse_week(t_hh, h_clases_hh)

    if t_turnen:
        week_rot.append(clases_turnen)
        week_blau.append(clases_turnen)

    week_rot += week_hh
    week_blau += week_hh


    # start_date = datetime.date(2020, 8, 10)

    calendars_to_generate = [
        (week_rot, start_date, 'rot-ipad.ics', False, None),
        (week_rot, start_date, 'rot-desktop.ics', True, None),
        (week_blau, start_date, 'blau-ipad.ics', False, None),
        (week_blau, start_date, 'blau-desktop.ics', True, None),
    ]

    if zoom_user:
        calendars_to_generate.append((
            week_rot, start_date,
            'rot-{}.ics'.format(zoom_user),
            False,
            zoom_user.replace(' ','%20')))

    for c in calendars_to_generate:
        generate_calendar(c[0], c[1], c[2], c[3], c[4])


def generate_calendar(week, start_date, ofile, scheme_desktop=True, uname=None):

    c = Calendar()
    for clase in week:

        e = Event()
        e.name = clase['curso']

        d_inc = datetime.timedelta(days=int(clase['day'])-1)

        t_begin = datetime.datetime(
            start_date.year,
            start_date.month,
            start_date.day,
            int(clase['hours']['t_start'][:2]),
            int(clase['hours']['t_start'][3:]),
            0,
        ) + d_inc

        t_end = datetime.datetime(
            start_date.year,
            start_date.month,
            start_date.day,
            int(clase['hours']['t_end'][:2]),
            int(clase['hours']['t_end'][3:]),
            0
        ) + d_inc

        e.begin = arrow.get(t_begin, TIME_ZONE)
        e.end = arrow.get(t_end, TIME_ZONE)
        # e.end = t_end.strftime("%Y-%m-%d %H:%M:%S")

        e.description = "ID: {}\nPWD: {}".format(
            clase['id'],
            clase['pwd']
        )

        if scheme_desktop:
            e.url = zoom_join_urlscheme_desktop(
                clase['id'],
                clase['pwd'],
                uname,
            )

        else:
            e.url = zoom_join_urlscheme_mobile(
                clase['id'],
                clase['pwd'],
                uname,
            )

        c.events.add(e)

    with open(ofile, 'w') as f:
        f.write(str(c))



def parse_week(t, hours):

    result = []

    s_days = [ '1', '2', '3', '4', '5',]
    s_hours = [str(i) for i in range(2, len(hours)+2)]


    for d in s_days:
        i_hour = 0
        for hour in s_hours:
            c = parse_class(t[d][hour])
            c['day'] = d
            c['hours'] = hours[i_hour]
            i_hour += 1
            result.append(c)

    return result


def parse_times(t):

    result = []

    hours = [str(i) for i in range(2, len(t['0']))]

    for h in hours:
        result.append(parse_time_line(t['0'][h]))

    return result


def day_to_number(s):

     l = {
        'LUNES': 1,
        'MARTES': 2,
        'MIERCOLES': 3,
        'MIÉRCOLES': 3,
        'JUEVES': 4,
        'VIERNES': 5,
        'SABADO': 6,
        'SÁBADO': 6,
        'DOMINGO': 7,
     }

     s = s.upper()
     return l.get(s, None)

def parse_time_turnen(t):

    result = {}
    result['curso'] = t['0']['0']
    day = day_to_number(t['0']['1'].split('\n')[1])
    if day:
        result['day'] = str(day)

    t_tmp = parse_time_line_turnen(t['0']['2'])
    result['hours'] = {
        't_start': t_tmp['t_start'],
        't_end' : t_tmp['t_end'],
    }
    result['id'] = t_tmp['id']
    result['pwd'] = t_tmp['pwd']

    return result


def parse_time_line_turnen(s):

    result = None

    regex = r"""^(?P<t_start>\d{2}:\d{2}).*ID:(?P<id>.*)(?P<t_end>\d{2}:\d{2}).*Contraseña:\s*(?P<pwd>\w+)"""
    s = s.replace('\n', '')
    p = re.compile(regex)
    m = p.match(s)

    if m:
        result = m.groupdict()
        result['id'] = result['id'].replace(' ', '')

    return result


def parse_time_line(s):

    regex = r"""^.*(?P<t_start>\d{2}:\d{2}).*(?P<t_end>\d{2}:\d{2})"""
    p = re.compile(regex)

    s = s.replace('\n', '')
    m = p.match(s)

    if m:
        return m.groupdict()
    else:
        return None


def parse_class(s):

    result = None
    # regex = r"""^(?P<curso>\w+)\s+\n\s*ID:\s*(?P<id>.*)\n.*:\s*(?P<pwd>\w+)"""
    regex = r"""^(?P<curso>\w+).*ID:(?P<id>.*)Contraseña:\s*(?P<pwd>\w+)"""
    p = re.compile(regex)
    m = p.match(s.replace('\n', ''))

    if m:
        result = m.groupdict()
        if 'curso' in result and 'id' in result and 'pwd' in result:
            result['id'] = result['id'].replace(' ','')  # eliminate spaces
    else:
        result = {
            'curso': s.split('\n')[0],
            'id': None,
            'pwd': None,
        }

    return result


def date_of_next_monday(start_date):
    next_monday = start_date + datetime.timedelta(days=7-start_date.weekday())
    return next_monday




if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Lee el archivo pdf con las clases de 1er grado, extrae los datos de las reuniones de Zoom y genera calendarios para los distintos grupos."
    )
    parser.add_argument('-d', '--date',
                        action='store',
                        help='Start date for the calendar.'
    )

    parser.add_argument('-f', '--file',
                        action='store',
                        required=True,
                        help='PDF file to process'
    )

    parser.add_argument('-u', '--uname',
                        action='store',
                        help="Zoom session's user name"
    )

    args = parser.parse_args()
    t_args = vars(args)

    if t_args.get('date'):
        start_date = datetime.datetime.strptime(t_args['date'],'%Y-%m-%d').date()
    else:
        start_date = date_of_next_monday(start_date=datetime.date.today())

    if DEBUG: print(start_date)

    if t_args.get('file'):
        fname = t_args['file']

    zoom_user = t_args.get('uname', None)

    if DEBUG: print(zoom_user)

    main(fname, start_date, zoom_user)
