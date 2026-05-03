import numpy as np
import pandas as pd
import os
from tkinter import Tk, messagebox
from process_temperature import process_temperature

def generate_temperature(folder, min_temp, max_temp, daily_variation, interval_seconds):
    total_days = 6
    total_hours = total_days * 24
    total_seconds = total_hours * 3600
    time_points = np.arange(0, total_seconds + interval_seconds, interval_seconds)

    increment_heating = (max_temp - min_temp - (6 * daily_variation)) / 5
    increment_cooling = abs(max_temp - min_temp - (6 * daily_variation)) / 5

    h_temp1 = min_temp
    h_temp2 = h_temp1 + daily_variation
    h_temp3 = h_temp2 + increment_heating
    h_temp4 = h_temp3 + daily_variation
    h_temp5 = h_temp4 + increment_heating
    h_temp6 = h_temp5 + daily_variation
    h_temp7 = h_temp6 + increment_heating
    h_temp8 = h_temp7 + daily_variation
    h_temp9 = h_temp8 + increment_heating
    h_temp10 = h_temp9 + daily_variation
    h_temp11 = h_temp10 + increment_heating
    h_temp12 = h_temp11 + daily_variation
    h_temp13 = h_temp12 + increment_heating

    heating_points = [
        (0, h_temp1),
        (43200, h_temp2),
        (86400, h_temp3),
        (129600, h_temp4),
        (172800, h_temp5),
        (216000, h_temp6),
        (259200, h_temp7),
        (302400, h_temp8),
        (345600, h_temp9),
        (388800, h_temp10),
        (432000, h_temp11),
        (475200, h_temp12),
        (518400, h_temp13)
    ]

    c_temp1 = max_temp
    c_temp2 = c_temp1 - daily_variation
    c_temp3 = c_temp2 + increment_cooling
    c_temp4 = c_temp3 - daily_variation
    c_temp5 = c_temp4 + increment_cooling
    c_temp6 = c_temp5 - daily_variation
    c_temp7 = c_temp6 + increment_cooling
    c_temp8 = c_temp7 - daily_variation
    c_temp9 = c_temp8 + increment_cooling
    c_temp10 = c_temp9 - daily_variation
    c_temp11 = c_temp10 + increment_cooling
    c_temp12 = c_temp11 - daily_variation
    c_temp13 = c_temp12 + increment_cooling

    cooling_points = [
        (0, c_temp1),
        (43200, c_temp2),
        (86400, c_temp3),
        (129600, c_temp4),
        (172800, c_temp5),
        (216000, c_temp6),
        (259200, c_temp7),
        (302400, c_temp8),
        (345600, c_temp9),
        (388800, c_temp10),
        (432000, c_temp11),
        (475200, c_temp12),
        (518400, c_temp13)
    ]

    heating_path = os.path.join(folder, "Temperature_Heating.csv")
    cooling_path = os.path.join(folder, "Temperature_Cooling.csv")

    root = Tk()
    root.withdraw()

    overwrite = True
    if os.path.exists(heating_path) or os.path.exists(cooling_path):
        answer = messagebox.askyesno("Overwrite Confirmation",
                                     "Temperature files already exist.\nDo you want to overwrite them?")
        overwrite = answer

    if overwrite:
        process_temperature(folder, heating_points, "Temperature_Heating", interval_seconds)
        process_temperature(folder, cooling_points, "Temperature_Cooling", interval_seconds)
        messagebox.showinfo("Success", "Temperature files generated successfully.")
    else:
        messagebox.showinfo("Canceled", "Operation canceled. Files were not overwritten.")

    root.destroy()
