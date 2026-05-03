import numpy as np

def calculate_declination(day_number):
    return 23.45 * np.sin(np.deg2rad((360.0 / 365.0) * (day_number - 81.0)))

def calculate_equation_of_time(day_number):
    B = np.deg2rad((360.0 / 365.0) * (day_number - 81.0))
    return 9.87 * np.sin(2 * B) - 7.53 * np.cos(B) - 1.5 * np.sin(B)

def calculate_hour_angle(latitude, longitude, time_zone, days, interval_seconds, mode="continuous"):
    seconds_per_day = 24 * 3600

    if mode == "continuous":
        total_seconds = len(days) * seconds_per_day
        t_rel = np.arange(0, total_seconds, interval_seconds)

        day_indices = np.floor(t_rel / seconds_per_day).astype(int)
        day_indices = np.clip(day_indices, 0, len(days) - 1)
        day_numbers = np.array(days)[day_indices]

        t_abs = t_rel % seconds_per_day

    elif mode == "cooling_cut":
        durations = [12 * 3600] + [24 * 3600] * (len(days) - 2) + [12 * 3600]
        cum_durations = np.cumsum([0] + durations)
        total_seconds = cum_durations[-1]

        t_rel = np.arange(0, total_seconds, interval_seconds)

        day_indices = np.searchsorted(cum_durations, t_rel, side="right") - 1
        day_indices = np.clip(day_indices, 0, len(days) - 1)
        day_numbers = np.array(days)[day_indices]

        time_within_segment = t_rel - cum_durations[day_indices]
        t_abs = time_within_segment

        t_abs = t_abs + (day_indices == 0) * (12 * 3600)
        t_abs = t_abs % seconds_per_day

    else:
        raise ValueError("Invalid mode. Use 'continuous' or 'cooling_cut'..")

    eot_hours = calculate_equation_of_time(day_numbers) / 60.0
    solar_time = (t_abs / 3600.0) + (longitude / 15.0) - time_zone + eot_hours
    hour_angles = 15.0 * (solar_time - 12.0)
    hour_angles = (hour_angles + 180) % 360 - 180

    declinations = calculate_declination(day_numbers)
    return t_rel, day_numbers, hour_angles, declinations
