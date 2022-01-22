from collections import Counter

def get_counter():
    return Counter(
        {
            "all": 0,
            "failed": 0,
            "invalid_label": 0,
            "too_short": 0,
            "too_long": 0,
            "imported_time": 0,
            "total_time": 0,
        }
    )


def get_imported_samples(counter):
    return (
        counter["all"]
        - counter["failed"]
        - counter["too_short"]
        - counter["too_long"]
        - counter["invalid_label"]
    )

def secs_to_hours(secs):
    hours, remainder = divmod(secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)

def print_import_report(counter, sample_rate, max_secs):
    print("Imported %d samples." % (get_imported_samples(counter)))
    if counter["failed"] > 0:
        print("Skipped %d samples that failed upon conversion." % counter["failed"])
    if counter["invalid_label"] > 0:
        print(
            "Skipped %d samples that failed on transcript validation."
            % counter["invalid_label"]
        )
    if counter["too_short"] > 0:
        print(
            "Skipped %d samples that were too short to match the transcript."
            % counter["too_short"]
        )
    if counter["too_long"] > 0:
        print(
            "Skipped %d samples that were longer than %d seconds."
            % (counter["too_long"], max_secs)
        )
    print(
        "Final amount of imported audio: %s from %s."
        % (
            secs_to_hours(counter["imported_time"] / sample_rate),
            secs_to_hours(counter["total_time"] / sample_rate),
        )
    )

