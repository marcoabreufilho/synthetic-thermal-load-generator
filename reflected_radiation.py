import numpy as np

def calculate_reflected_radiation(albedo, beta_deg, source_name,
                                  I_global, inclined_dict,
                                  target_name, I_target_inclined):
    beta = np.radians(beta_deg)

    if source_name == "Ground":
        I_source = I_global
    elif source_name in inclined_dict:
        I_source = inclined_dict[source_name]
    else:
        raise ValueError(f"Source '{source_name}' not found.")

    G_r_base = albedo * I_source * (1 - np.cos(beta)) / 2

    incidence_factor = np.clip(I_target_inclined / np.max(I_target_inclined), 0, 1)

    G_r = G_r_base * incidence_factor
    G_r[I_target_inclined <= 0] = 0

    return G_r

