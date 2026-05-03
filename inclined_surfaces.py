import numpy as np

def calculate_inclined_irradiance(I_horizontal, latitude, declination, hour_angle, beta, gamma):

    phi = np.radians(latitude)
    delta = np.radians(declination)
    h = np.radians(hour_angle)
    beta = np.radians(beta)
    gamma = np.radians(gamma)

    cos_theta_i = (
        np.sin(phi) * np.sin(delta) * np.cos(beta)
        - np.cos(phi) * np.sin(delta) * np.sin(beta) * np.cos(gamma)
        + np.cos(phi) * np.cos(delta) * np.cos(h) * np.cos(beta)
        + np.sin(phi) * np.cos(delta) * np.cos(h) * np.sin(beta) * np.cos(gamma)
        + np.cos(delta) * np.sin(h) * np.sin(beta) * np.sin(gamma)
    )

    return I_horizontal * np.maximum(cos_theta_i, 0)
