"""Google Sheet Writer"""

import datetime
from enum import Enum

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from . import mailer
import helper, const, config


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    NEW_LINE = 2


INITIAL_CELL = (2, 2)


def get_gsheet_client(client_secret):
    creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret, const.GSHEET_SCOPE)
    client = gspread.authorize(creds)
    return client


def get_spreadsheet(client_secret, spreadsheet_key):
    client = get_gsheet_client(client_secret)
    return client.open_by_key(spreadsheet_key)


def get_worksheet(spreadsheet, title):
    """Get the most recent worksheet in the specified spreadsheet.
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
    """Return reference to the next empty cell.
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
            curr_cell = increment_row(curr_cell)
            val_second = worksheet.cell(curr_cell[0], curr_cell[1]).value
            # Found the second empty cell
            if val_second == '':
                empty = True
            else:
                curr_cell = increment_row(curr_cell)
        else:
            curr_cell = increment_row(curr_cell)
    return curr_cell


def increment_row(coordinates):
    coordinates[0] = coordinates[0] + 1
    return coordinates


def increment_column(coordinates):
    coordinates[1] = coordinates[1] + 1
    return coordinates


def increment_line_and_restart(coordinates):
    coordinates = increment_row(coordinates)
    coordinates[1] = INITIAL_CELL[1]
    return coordinates


def write(worksheet, cell, data, direction):
    if not isinstance(direction, Direction):
        raise TypeError('direction must be an instance of Direction Enum')

    worksheet.update_cell(cell[0], cell[1], data)
    if direction == Direction.RIGHT:
        cell = increment_column(cell)
    if direction == Direction.DOWN:
        cell = increment_row(cell)
    if direction == Direction.NEW_LINE:
        cell = increment_line_and_restart(cell)
    return cell


def fill(worksheet, title, workout):
    curr_cell = get_next_empty_cell(worksheet)

    # Fill out date and title
    curr_cell = write(worksheet, curr_cell, get_today_date(), Direction.DOWN)
    curr_cell = write(worksheet, curr_cell, title, Direction.DOWN)
    exercises_cell = curr_cell[:]

    # Fill out workout info
    for name, details in workout.items():
        curr_cell = fill_exercise(worksheet, name, details, curr_cell)
        curr_cell = increment_line_and_restart(curr_cell)

    check_for_errors(worksheet, exercises_cell)


def fill_exercise(worksheet, name, details, curr_cell):
    # Only name and rep range
    if len(details) == 1:
        curr_cell = write(worksheet, curr_cell, name, Direction.RIGHT)
        curr_cell = write(worksheet, curr_cell, details[0], Direction.RIGHT)

    # More details than just the rep range
    else:
        # Write exercise name and save the next cell's location for rep range
        curr_cell = write(worksheet, curr_cell, name, Direction.RIGHT)
        note_cell = curr_cell[:]

        # Move two spots to the right
        for i in range(2):
            curr_cell = increment_column(curr_cell)

        # Rep range cell might not be in order, that's why it needs to go to previously referenced cell
        for note in details:
            if helper.is_rep_range(note):
                write(worksheet, note_cell, note, Direction.RIGHT)
            else:
                curr_cell = write(worksheet, curr_cell, note, Direction.RIGHT)
    return curr_cell


def check_for_errors(worksheet, cell) -> bool:
    """

    """
    finished = False
    report = False
    rep_range_cell = cell[:]
    rep_range_cell = increment_column(rep_range_cell)

    while not finished:
        val = worksheet.cell(cell[0], cell[1]).value
        if not val == '':
            cell_col = cell[:]
            cell_col = increment_column(cell_col)
            val_col = worksheet.cell(cell_col[0], cell_col[1]).value
            if val_col == '':
                report = True
                finished = True
            cell = increment_row(cell)
        else:
            cell = increment_row(cell)
            val2 = worksheet.cell(cell[0], cell[1]).value
            if val2 == '':
                finished = True
            else:
                report = True
                finished = True

    # Missing one error case where the last exercise name is missing name, but has a rep range - never happened so far
    if report:
        message = "There is something wrong with today's Daily Pump."
        mailer.send_mail(message, config.SENDER_EMAIL, config.RECEIVER_EMAIL)
