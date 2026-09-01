"""
Frozen constants required by the Step3R2D source-anchored mission evaluator.

These values are ported from reference implementation InputConditions and Step3R2D_config.
Only quantities needed by the current mission/mass evaluator are included.
"""

GAMMA = 1.4
RA_J_PER_KG_K = 287.0
G_MPS2 = 9.81

FIRST_STAGE_ROCKET_ISP_S = 341.0
SECOND_STAGE_ROCKET_ISP_S = 442.0

ORBIT_VELOCITY_MPS = 7780.0
ORBIT_ALTITUDE_KM = 200.0
TAKEOFF_ALTITUDE_KM = 0.0

PAYLOAD_MASS_T = 8.0
SIGMA1ST_RBCC = 0.42
SIGMA2ND = 0.238

PENALTY = 1e12
DEN_TOL = 1e-10
PHYSICAL_TOL = 1e-10
