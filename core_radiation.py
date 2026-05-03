import os
import pandas as pd
import numpy as np
from tkinter import messagebox, Tk

from hour_angle import calculate_hour_angle
from global_diffuse import calculate_global_diffuse_radiation
from inclined_surfaces import calculate_inclined_irradiance
from reflected_radiation import calculate_reflected_radiation


def _month_to_doy_lists():

    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    month_days = {}
    doy_start = 1
    for m, ndays in enumerate(month_lengths, start=1):
        month_days[m] = list(range(doy_start, doy_start + ndays))
        doy_start += ndays

    return month_days


def _months_end_at(end_m, n):
    return [((end_m - n + i - 1) % 12) + 1 for i in range(1, n + 1)]


def _months_start_at(start_m, n):
    return [((start_m - 1 + i) % 12) + 1 for i in range(n)]


def _monthly_mean_day(latitude, longitude, time_zone,
                      solar_constant, clearness_index,
                      interval_seconds, month_days):

    time, day, ha, decl = calculate_hour_angle(
        latitude, longitude, time_zone, month_days, interval_seconds, mode="continuous"
    )

    _, global_rad, diffuse_rad = calculate_global_diffuse_radiation(
        latitude, decl, ha, day, solar_constant, clearness_index
    )

    df = pd.DataFrame({
        "TimeOfDay": np.array(time) % 86400,  # garante hora do dia para média ponto-a-ponto
        "Hour Angle (°)": ha,
        "Declination (°)": decl,
        "Global Radiation (W/m²)": global_rad,
        "Diffuse Radiation (W/m²)": diffuse_rad
    })

    mean_df = df.groupby("TimeOfDay", as_index=False).mean(numeric_only=True)

    time_of_day = mean_df["TimeOfDay"].to_numpy()
    g = mean_df["Global Radiation (W/m²)"].to_numpy()
    d = mean_df["Diffuse Radiation (W/m²)"].to_numpy()
    ha_m = mean_df["Hour Angle (°)"].to_numpy()
    decl_m = mean_df["Declination (°)"].to_numpy()

    peak = float(np.max(g))
    return time_of_day, g, d, ha_m, decl_m, peak


def generate_radiation(folder,
                       latitude, longitude, time_zone,
                       solar_constant,
                       clearness_index_heating,
                       clearness_index_cooling,
                       interval_seconds,
                       surfaces=None,
                       reflected_surfaces=None,
                       generate_self_shadowing_inputs=False):

    os.makedirs(folder, exist_ok=True)
    month_days_map = _month_to_doy_lists()

    selection_kt = clearness_index_heating

    monthly_peaks = {}
    for m in range(1, 13):
        _, _, _, _, _, peak = _monthly_mean_day(
            latitude, longitude, time_zone,
            solar_constant, selection_kt,
            interval_seconds, month_days_map[m]
        )
        monthly_peaks[m] = peak

    critical_month = max(monthly_peaks, key=monthly_peaks.get)

    # Heating:
    heating_months = _months_end_at(critical_month, 6)
    # Cooling:
    cooling_months = _months_start_at(critical_month, 7)

    monthly_mean_heating = {}
    for m in set(heating_months):
        monthly_mean_heating[m] = _monthly_mean_day(
            latitude, longitude, time_zone,
            solar_constant, clearness_index_heating,
            interval_seconds, month_days_map[m]
        )

    monthly_mean_cooling = {}
    for m in set(cooling_months):
        monthly_mean_cooling[m] = _monthly_mean_day(
            latitude, longitude, time_zone,
            solar_constant, clearness_index_cooling,
            interval_seconds, month_days_map[m]
        )

    def build_heating_series(month_list):
        T_all, G_all, D_all, HA_all, DECL_all = [], [], [], [], []
        for i, m in enumerate(month_list):
            tod, g, d, ha, decl, _ = monthly_mean_heating[m]
            t = tod + i * 86400.0
            T_all.append(t)
            G_all.append(g)
            D_all.append(d)
            HA_all.append(ha)
            DECL_all.append(decl)
        return (np.concatenate(T_all), np.concatenate(G_all), np.concatenate(D_all),
                np.concatenate(HA_all), np.concatenate(DECL_all))

    def build_cooling_cut_series(month_list_7):

        T_all, G_all, D_all, HA_all, DECL_all = [], [], [], [], []
        t_offset = 0.0
        HALF = 43200.0
        FULL = 86400.0

        for j, m in enumerate(month_list_7):
            tod, g, d, ha, decl, _ = monthly_mean_cooling[m]

            if j == 0:
                mask = tod >= HALF
                tod_sel = tod[mask] - HALF
                duration = HALF
            elif j == len(month_list_7) - 1:
                mask = tod < HALF
                tod_sel = tod[mask]
                duration = HALF
            else:
                mask = slice(None)
                tod_sel = tod
                duration = FULL

            g_sel = g[mask] if isinstance(mask, np.ndarray) else g
            d_sel = d[mask] if isinstance(mask, np.ndarray) else d
            ha_sel = ha[mask] if isinstance(mask, np.ndarray) else ha
            decl_sel = decl[mask] if isinstance(mask, np.ndarray) else decl

            t = tod_sel + t_offset

            T_all.append(t)
            G_all.append(g_sel)
            D_all.append(d_sel)
            HA_all.append(ha_sel)
            DECL_all.append(decl_sel)

            t_offset += duration

        return (np.concatenate(T_all), np.concatenate(G_all), np.concatenate(D_all),
                np.concatenate(HA_all), np.concatenate(DECL_all))

    time_h, global_h, diffuse_h, ha_h, decl_h = build_heating_series(heating_months)
    time_c, global_c, diffuse_c, ha_c, decl_c = build_cooling_cut_series(cooling_months)

    df_h = pd.DataFrame({
        "Time (s)": time_h,
        "Global Radiation (W/m²)": global_h,
        "Diffuse Radiation (W/m²)": diffuse_h
    })

    df_c = pd.DataFrame({
        "Time (s)": time_c,
        "Global Radiation (W/m²)": global_c,
        "Diffuse Radiation (W/m²)": diffuse_c
    })

    inclined_dict_h = {}
    inclined_dict_c = {}

    if surfaces:
        for surface in surfaces:
            name = surface["name"]
            beta = surface["inclination"]
            gamma = surface["azimuth"]

            col_h = calculate_inclined_irradiance(global_h, latitude, decl_h, ha_h, beta, gamma)
            col_c = calculate_inclined_irradiance(global_c, latitude, decl_c, ha_c, beta, gamma)

            df_h[f"Inclined Radiation {name} (W/m²)"] = col_h
            df_c[f"Inclined Radiation {name} (W/m²)"] = col_c

            inclined_dict_h[name] = col_h
            inclined_dict_c[name] = col_c

    if reflected_surfaces:
        for r in reflected_surfaces:
            name = r["name"]
            beta = r["inclination"]
            albedo = r["albedo"]
            source = r["source"]

            I_target_h = inclined_dict_h.get(name, global_h)
            I_target_c = inclined_dict_c.get(name, global_c)

            G_r_h = calculate_reflected_radiation(albedo, beta, source, global_h, inclined_dict_h, name, I_target_h)
            G_r_c = calculate_reflected_radiation(albedo, beta, source, global_c, inclined_dict_c, name, I_target_c)

            df_h[f"Reflected Radiation {name} from {source} (W/m²)"] = G_r_h
            df_c[f"Reflected Radiation {name} from {source} (W/m²)"] = G_r_c

    if generate_self_shadowing_inputs:
        def save_shadowing(time, ha, decl, filename):
            df_shadow = pd.DataFrame({
                "Time (s)": time,
                "Hour Angle (°)": ha,
                "Declination (°)": decl
            })
            df_shadow.to_csv(os.path.join(folder, filename), index=False, encoding="utf-8-sig")

        save_shadowing(time_h, ha_h, decl_h, "Self_Shadowing_Inputs_Heating.csv")
        save_shadowing(time_c, ha_c, decl_c, "Self_Shadowing_Inputs_Cooling.csv")

    heating_path = os.path.join(folder, "Radiation_Heating.csv")
    cooling_path = os.path.join(folder, "Radiation_Cooling.csv")

    root = Tk()
    root.withdraw()

    overwrite = True
    if os.path.exists(heating_path) or os.path.exists(cooling_path):
        answer = messagebox.askyesno("Overwrite Confirmation",
                                     "Radiation files already exist.\nDo you want to overwrite them?")
        overwrite = answer

    if overwrite:
        df_h.to_csv(heating_path, index=False, encoding="utf-8-sig")
        df_c.to_csv(cooling_path, index=False, encoding="utf-8-sig")
        messagebox.showinfo("Success", "Radiation files generated successfully.")
    else:
        messagebox.showinfo("Canceled", "Operation canceled. Files were not overwritten.")

    root.destroy()

