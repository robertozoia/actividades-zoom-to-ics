import datetime
import argparse
import primer_grado

DEBUG = True


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

    parser.add_argument('-p', '--prefix',
                        action='store',
                        required=False,
                        help='A string that will be prepended to calendar files.'
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

    if t_args.get('prefix', None):
        cal_file_prefix = t_args['prefix']
    else:
        cal_file_prefix = None

    if DEBUG: print(zoom_user)

    primer_grado.gen_1grado(fname, start_date, zoom_user, cal_file_prefix)
