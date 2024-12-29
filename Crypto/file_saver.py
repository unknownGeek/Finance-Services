import os

base_directory = '/Users/h0k00sn/Documents/Projects/py/Crypto/resources/crypto-reports'


def create_date_directory(startDateTime):
    """Creates a main directory for the current date."""
    current_date = startDateTime.strftime('%Y-%m-%d')
    date_directory = os.path.join(base_directory, current_date)  # Main directory for the date

    # Create the date directory if it doesn't exist
    if not os.path.exists(date_directory):
        os.makedirs(date_directory)

    return date_directory


def create_run_directory(date_directory, startDateTime):
    """Creates a unique run directory based on the current time and item count."""
    existing_runs = [d for d in os.listdir(date_directory) if os.path.isdir(os.path.join(date_directory, d))]
    item_count = len(existing_runs) + 1  # Increment count for the new run

    current_time = startDateTime.strftime('%Y%m%d_%H%M%S')  # Format: YYYYMMDD_HHMMSS
    run_directory = os.path.join(date_directory, f'run_{item_count}_{current_time}')  # Subdirectory for the run

    # Create the run directory if it doesn't exist
    if not os.path.exists(run_directory):
        os.makedirs(run_directory)

    return run_directory


def save_to_csv(dataframe, directory, filename):
    """Saves a DataFrame to a CSV file in the specified directory."""
    full_path = os.path.join(directory, filename)  # Combine directory and filename
    dataframe.to_csv(full_path, index=False)
    print(f'{filename} saved to {full_path}\n')
