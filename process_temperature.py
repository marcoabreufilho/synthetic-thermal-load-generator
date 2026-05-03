import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
from scipy.signal import savgol_filter
import os


def process_temperature(folder, points, filename, interval_seconds):
    points = np.array(points)

    extended_points = np.vstack([
        [points[0, 0] - 1, points[0, 1]],
        points,
        [points[-1, 0] + 1, points[-1, 1]]
    ])

    x = extended_points[:, 0]
    y = extended_points[:, 1]

    interpolator = PchipInterpolator(x, y)

    time_final = 518400
    time_output = np.arange(0, time_final + interval_seconds, interval_seconds)

    temperature_output = interpolator(time_output)

    window_size = 51 if len(time_output) >= 51 else len(time_output) - (len(time_output) + 1) % 2
    if window_size > 3:
        temperature_output = savgol_filter(temperature_output, window_size, 3)

    df = pd.DataFrame({
        "Time (s)": time_output,
        "Temperature (°C)": temperature_output
    })

    output_path = os.path.join(folder, f"{filename}.csv")
    df.to_csv(output_path, index=False, encoding='utf-8-sig', float_format="%.4f")

