import re

from bs4 import BeautifulSoup

# Regular expressions to match rep range formats (eg. 4 sets of 10; 12,10,8,8; 3 sets to Failure; 15/15,12/12,10/10)

set_expression = re.compile(r'\d+\sset')
num_of_reps_expr = re.compile(r'\d+,\d+')
superset_expr = re.compile(r'\d+/\d+,')

is_rep_range_regex = re.compile(r'(\d+\sset)|(\d+,\d+)|(\d+/\d+,)')


def is_rep_range(text: str) -> bool:
    return is_rep_range_regex.search(text) is not None


def get_block():
    """Return a local version of a workout block soup."""
    return BeautifulSoup(HTML, 'html.parser')

def get_split():
    """Return a local version of a split block soup."""
    return BeautifulSoup(LOCAL_SPLIT, 'html.parser')


HTML = """<div class=\"sqs-block-content\"><h1 style=\"text-align: center; white-space: pre-wrap;\">Biceps/triceps</h1>
<p style=\"text-align: center; white-space: pre-wrap;\"><strong>Machine Preacher Curl<br/></strong>12,10,8,10,12<br/>
<br/>*<strong>Machine Tricep Press Down<br/></strong>12,10,8,10,12<br/><br/><strong>Seated Double Arm Dumbbell Curl
<br/></strong>15,12,10,12,15<br/><br/><strong>Incline Bench Barbell Skull Crusher<br/></strong>15,12,10,12,15<br/><br/>
<strong>Barbell Curl<br/></strong>(Shoulder width grip)<strong><br/></strong>10,8,6,6<br/><br/><strong>
Tricep Cable Press Down<br/></strong>(Shoulder width, reverse grip)<strong><br/></strong>10,8,6,6<br/><br/><strong>
Bent Over Dumbbell Concentration Curl<br/></strong>4 sets of 15<br/><br/><strong>Single Arm Tricep Press Down<br/>
</strong>(Rope attachment)<strong><br/></strong>4  sets of 15</p></div>"""


LOCAL_SPLIT = """<div class=\"sqs-block-content\"><h1 style=\"text-align: center; white-space: pre-wrap;\">
CURRENT Split</h1><p style=\"text-align: center; white-space: pre-wrap;\">As of November 4th 2018</p>
<p style=\"text-align: center; white-space: pre-wrap;\"><strong>Day 1</strong><br/>Quads/Adductors<br/>
<br/><strong>Day 2</strong><br/>Chest/Forearms/Light Shoulders</p><p style=\"text-align: center; 
white-space: pre-wrap;\"><strong>Day 3</strong><br/>Back/Traps</p><p style=\"text-align: center; 
white-space: pre-wrap;\"><strong>Day 4</strong><br/>Calves/Abs/Neck</p><p style=\"text-align: center; 
white-space: pre-wrap;\"><strong>Day 5</strong><br/>Hamstrings/Glutes/Abductors/Light Chest<br/><br/>
<strong>Day 6</strong><br/>Shoulders/Light Back<br/><br/><strong>Day 7</strong><br/>Biceps/Triceps<br/>
<br/></p><h1 style=\"text-align: center; white-space: pre-wrap;\">@SMITH.JULIAN</h1></div>"""