"""Google Sheet Writer

Fills out data in the selected worksheet.
Moves a cursor around in the sheet, using Direction Enum, to prevent overwriting the same cell.
"""

import datetime
from enum import Enum

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import const
from . import mailer, helper


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    NEW_LINE = 2


INITIAL_CELL = [2, 2]


def get_gsheet_client(client_secret):
    creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret, const.GSHEET_SCOPE)
    client = gspread.authorize(creds)
    return client


def get_spreadsheet(client_secret, spreadsheet_key):
    client = get_gsheet_client(client_secret)
    return client.open_by_key(spreadsheet_key)


def get_worksheet(spreadsheet, title):
    """
    Get the most recent worksheet in the specified spreadsheet.
    If the title of the workout points to a new week, creates a new worksheet.
    """
    if title == const.FIRST_DAY:
        worksheet = create_new_week_worksheet(spreadsheet)
    else:
        worksheet = spreadsheet.worksheets()[-1]
    return worksheet


def create_new_week_worksheet(spreadsheet):
    """Create a new worksheet where the name is the week of the year."""
    if get_day_of_week == 1:
        week = get_week_of_year()
    else:
        week = get_week_of_year(6)
    title = 'Week ' + str(week)
    return spreadsheet.add_worksheet(title, 300, 20)


def get_today_date():
    return datetime.date.today().strftime("%B %d, %Y")


def get_day_of_week():
    return datetime.date.today().isocalendar()[2]


def get_week_of_year(offset=0):
    return datetime.date.today().isocalendar()[1]


def get_next_empty_cell(worksheet) -> list:
    """
    Return reference to the next empty cell.
    Looks for the next empty vertical cell. Makes sure that there are two empty cells after the last cell with content.
    """
    curr_cell = list(INITIAL_CELL)
    if worksheet.cell(*curr_cell).value == '':
        return curr_cell

    empty = False
    while not empty:
        val = worksheet.cell(*curr_cell).value

        # Found the first empty cell
        if val == '':
            _increment_cell_row(curr_cell)
            val_second = worksheet.cell(*curr_cell).value
            # Found the second empty cell
            if val_second == '':
                empty = True
            else:
                _increment_cell_row(curr_cell)
        else:
            _increment_cell_row(curr_cell)
    return curr_cell


def write(worksheet, cell, data, direction):
    """Write data to the given cell. Then update the cell cursor in the given direction."""
    worksheet.update_cell(cell[0], cell[1], data)
    _move_cell(cell, direction)


def fill(worksheet, title, workout):
    """Fill out the sheet with the title and workout details."""
    curr_cell = get_next_empty_cell(worksheet)
    fill_date_and_title(worksheet, curr_cell, title)
    exercises_cell = curr_cell[:]
    for name, details in workout.items():
        fill_exercise(worksheet, name, details, curr_cell)
        _increment_line_and_restart(curr_cell)

    if check_for_errors(worksheet, exercises_cell):
        message = "There is something wrong with today's Daily Pump."
        mailer.send_mail(message, 'mailToReceive@updates.com')


def fill_date_and_title(worksheet, cell, title):
    """Fill out current date and workout title"""
    write(worksheet, cell, get_today_date(), Direction.DOWN)
    write(worksheet, cell, title, Direction.DOWN)


def fill_exercise(worksheet, name, details, curr_cell):
    """Fill out exercise detail portion of the workout."""
    # Only name and rep range
    if len(details) == 1:
        write(worksheet, curr_cell, name, Direction.RIGHT)
        write(worksheet, curr_cell, details[0], Direction.RIGHT)

    # More details than just the rep range
    else:
        # Write exercise name and save the next cell's location for rep range
        write(worksheet, curr_cell, name, Direction.RIGHT)
        note_cell = curr_cell[:]

        # Move two spots to the right
        for i in range(2):
            _increment_cell_column(curr_cell)

        # Rep range cell might not be in order, that's why it needs to go to previously referenced cell
        for note in details:
            if helper.is_rep_range(note):
                write(worksheet, note_cell, note, Direction.RIGHT)
            else:
                write(worksheet, curr_cell, note, Direction.RIGHT)
    return curr_cell


def check_for_errors(worksheet, cell) -> bool:
    """
    Check if there are any missing cells in the newly filled out sheet.
    """
    errors_found = False
    rep_range_cell = cell[:]
    _increment_cell_column(rep_range_cell)

    finished = False
    while not finished:
        val = worksheet.cell(*rep_range_cell).value
        if not val == '':
            cell_col = rep_range_cell[:]
            _increment_cell_column(cell_col)
            val_col = worksheet.cell(*cell_col).value
            if val_col == '':
                errors_found = True
                finished = True
            _increment_cell_row(rep_range_cell)
        else:
            _increment_cell_row(rep_range_cell)
            val2 = worksheet.cell(*rep_range_cell).value
            if val2 == '':
                finished = True
            else:
                errors_found = True
                finished = True

    return errors_found


def _move_cell(cell, direction):
    """Move a cursor in the sheet in a given direction.

    :param cell: Cell coordinates [row, col]
    :param direction: Direction in which to move the cell
    """
    if not isinstance(direction, Direction):
        raise TypeError('direction must be an instance of Direction Enum')
    if direction == Direction.RIGHT:
        _increment_cell_column(cell)
    if direction == Direction.DOWN:
        _increment_cell_row(cell)
    if direction == Direction.NEW_LINE:
        _increment_line_and_restart(cell)


def _increment_cell_row(coordinates):
    coordinates[0] += 1


def _increment_cell_column(coordinates):
    coordinates[1] += 1


def _increment_line_and_restart(coordinates):
    _increment_cell_row(coordinates)
    coordinates[1] = INITIAL_CELL[1]
