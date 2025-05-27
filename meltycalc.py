import math

def calculate_spinup_with_current_limit(
    disc_diameter_in,
    wheel_diameter_in,
    contact_radius_in,
    mass_lb,
    single_wheel_stall_torque_nm,
    number_of_wheels,
    stall_current_a,
    current_limit_a,
    max_wheel_rpm
):
    # Convert units
    disc_radius_m = (disc_diameter_in / 2) * 0.0254
    wheel_radius_m = (wheel_diameter_in / 2) * 0.0254
    contact_radius_m = contact_radius_in * 0.0254
    mass_kg = mass_lb * 0.453592

    # Moment of inertia for solid disc: I = 0.5 * m * r^2
    I = 0.5 * mass_kg * disc_radius_m**2

    # Convert max wheel RPM to rad/s
    max_wheel_rad_per_sec = max_wheel_rpm * 2 * math.pi / 60

    # Radius ratio
    radius_ratio = contact_radius_m / wheel_radius_m

    # Max disc angular velocity (rad/s)
    max_disc_rad_per_sec = max_wheel_rad_per_sec / radius_ratio

    # Total torque limited by current
    limited_torque_nm = single_wheel_stall_torque_nm * (current_limit_a / stall_current_a)
    total_limited_torque_nm = limited_torque_nm * number_of_wheels
    torque_constant = total_limited_torque_nm * radius_ratio
    slope = radius_ratio / max_wheel_rad_per_sec

    A = torque_constant / I
    B = slope

    def time_to_omega(omega_target):
        if omega_target >= max_disc_rad_per_sec:
            return math.inf
        return - (1 / (A * B)) * math.log(1 - B * omega_target)

    def rpm_to_rad_per_sec(rpm):
        return rpm * 2 * math.pi / 60

    def rad_per_sec_to_rpm(rad_per_sec):
        return rad_per_sec * 60 / (2 * math.pi)

    def kinetic_energy(omega_val):
        return 0.5 * I * omega_val**2

    test_rpms = [750, 1000, 1500, 2000, int(rad_per_sec_to_rpm(max_disc_rad_per_sec))]

    results = []
    for rpm in test_rpms:
        omega_target = rpm_to_rad_per_sec(rpm)
        t = time_to_omega(omega_target)
        KE = kinetic_energy(omega_target)
        KE_per_lb = KE / mass_lb
        results.append({
            "rpm": rpm,
            "time_s": t if t != math.inf else float('inf'),
            "kinetic_energy_j": KE,
            "joules_per_pound": KE_per_lb
        })

    return {
        "max_disc_rpm": rad_per_sec_to_rpm(max_disc_rad_per_sec),
        "results": results
    }

# Example usage
params = {
    "disc_diameter_in": 18,
    "wheel_diameter_in": 3,
    "contact_radius_in": 8,
    "mass_lb": 30,
    "single_wheel_stall_torque_nm": 1.17,
    "number_of_wheels": 4,
    "stall_current_a": 130,
    "current_limit_a": 100,
    "max_wheel_rpm": 19500
}

results = calculate_spinup_with_current_limit(**params)
print(f"Max disc RPM: {results['max_disc_rpm']:.2f}")
for r in results['results']:
    print(f"RPM: {r['rpm']} - Time: {r['time_s']:.2f} s - KE: {r['kinetic_energy_j']:.1f} J - J/lb: {r['joules_per_pound']:.1f}")
