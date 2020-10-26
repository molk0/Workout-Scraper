import re


# Regular expressions to match rep range formats (eg. 4 sets of 10; 12,10,8,8; 3 sets to Failure; 15/15,12/12,10/10)
set_expression = re.compile(r'\d+\sset')
num_of_reps_expr = re.compile(r'\d+,\d+')
superset_expr = re.compile(r'\d+/\d+,')

master_expression = "|".join([set_expression, num_of_reps_expr, superset_expr])


def is_rep_range(text: str) -> bool:
	return bool(master_expression.search(text))
