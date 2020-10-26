"""
Module used to parse the website and extract the workout details from it.
"""

import bs4
import requests
from bs4 import BeautifulSoup

import config, const


def get_soup_from_website():
    website = requests.get(config.SITE_LINK, auth=(config.SITE_LINK, config.SITE_PASSWORD))
    return BeautifulSoup(website.text, 'html.parser')


def get_workout_block():
    soup = get_soup_from_website()
    block = soup.find_all('div', class_='sqs-block-content')
    return block[1]


def get_workout_split_definition_block(souped_site):
    block = souped_site.find_all('div', class_='sqs-block-content')
    return block[8]


def get_title_and_workout_details(workout_block) -> tuple:
    title = get_workout_title(workout_block)
    details = extract_workout_details(workout_block)
    workout= get_workout(details)
    return title, workout


def get_workout_title(workout_block):
    return workout_block.h1.text.upper()


def extract_workout_details(workout_block):
    """Return a list of exercises followed by their rep range, and any details (such as tempo, attachment, stance).
    It iterates through children under <p> tag. The list includes some unnecessary elements (like empty </br> tags)
    that will need to be removed.

    Formatted list of exercises, followed by any information pertaining to the exercise.
    Each exercise is separated by an empty line, ""
    """
    details = []
    exercise_block = workout_block.p
    for child in exercise_block.children:
        if type(child) is bs4.element.Tag:
            details.append(str(child.text).replace('\n', ''))
        if type(child) is bs4.element.NavigableString:
            details.append(str(child))
    return clean_up_exercises(details)


def clean_up_exercises(exercise_details):
    """Remove all unnecessary elements, separating exercises by an empty character."""
    formatted_list = []
    for counter, detail in enumerate(exercise_details):
        if detail == "":
            counter = counter + 1
            if counter == len(exercise_details):
                break

            if exercise_details[counter] == "":
                formatted_list.append("")
                continue
        elif "*" in detail:
            continue
        else:
            formatted_list.append(detail)

    formatted_list.append('')
    return formatted_list


def get_workout(exercise_details: list) -> dict:
    """Return a dictionary, where they key is an exercise, and the values include is a tuple of rep ranges, and
    additional notes.

    :param exercise_details: Exercise list, with exercise name followed by rep ranges and details.
                             Exercises separated by ''.
    :return: Dictionary where name of the exercise is they key, and the value is a list with the exercise details
    """
    title_added = False
    data, current_list = {}, []
    index = 2
    for element in exercise_details:
        if element == '\n':
            continue

        if not title_added:
            title = element
            if title in data:
                title = ''.join((title, ' #', str(index)))
                index += 1
            title_added = True
            continue
        if element == '':
            data[title] = current_list
            current_list = []
            title_added = False
            continue
        current_list.append(element)
    print(data)
    return data


def get_local_block():
    return BeautifulSoup(const.HTML, 'html.parser')


def get_local_split():
    return BeautifulSoup(const.LOCAL_SPLIT, 'html.parser')


def get_first_split_day(split_block):
    return split_block.find('br').next_sibling.upper()
