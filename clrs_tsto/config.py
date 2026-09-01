from dataclasses import dataclass


@dataclass(frozen=True)
class TrajectoryConfig:
    """
    Frozen source-anchored trajectory configuration.

    Values are ported directly from reference implementation Step3R2D_config.
    """

    LowMidAnchorMach: float = 2.5
    LowMidAnchorAltitude_km: float = 15.0
    HighMachStartMach: float = 6.0
    HighMachReferenceDynamicPressure_Pa: float = 95.8e3


DEFAULT_TRAJECTORY_CONFIG = TrajectoryConfig()