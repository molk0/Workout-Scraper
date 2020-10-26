import config
from scraper import pump, gsheets

if __name__ == "__main__":
    # LOCAL
    # workout_block = pump.get_local_block()

    # REMOTE
    workout_block = pump.get_workout_block()

    title, workout = pump.get_title_and_workout_details(workout_block)

    print("Starting...")
    spreadsheet = gsheets.get_spreadsheet(config.CLIENT_SECRET, config.SPREADSHEET_KEY)
    worksheet = gsheets.get_worksheet(spreadsheet, title)
    gsheets.fill(worksheet, title, workout)
    print("Workout saved.")
