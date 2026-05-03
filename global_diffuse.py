import numpy as np

def calculate_global_diffuse_radiation(latitude, declination, hour_angle, day_of_year, solar_constant, clearness_index):
    clearness_index = np.clip(clearness_index, 0.05, 0.95)

    etr = solar_constant * (1 + 0.033 * np.cos(2 * np.pi * day_of_year / 365)) * (
        np.cos(np.radians(latitude)) * np.cos(np.radians(declination)) * np.cos(np.radians(hour_angle)) +
        np.sin(np.radians(latitude)) * np.sin(np.radians(declination))
    )

    etr = np.maximum(etr, 0)
    global_radiation = clearness_index * etr

    kd = 0.9888 + 0.3950 * clearness_index - 3.7003 * clearness_index**2 + 2.2905 * clearness_index**3
    diffuse_radiation = kd * global_radiation

    diffuse_radiation = np.minimum(diffuse_radiation, global_radiation)

    return etr, global_radiation, diffuse_radiation

