"""Product views for Analysis II, separate from frozen generator identity."""

MATRIX: dict[str, dict[int, tuple[str, ...]]] = {
    "improper-integrals": {
        1: ("improper-p-test",),
        2: ("improper-power-tail", "improper-exponential"),
        3: ("improper-comparison", "improper-arctangent"),
        4: ("improper-log-test", "improper-divergence"),
        5: ("improper-decay-mass", "improper-volume"),
    },
    "series": {
        1: ("series-p-test", "series-term-test"),
        2: ("series-alternating", "series-comparison", "series-root-test"),
        3: ("series-ratio-test", "series-log-test", "series-power-radius"),
        4: ("series-power-interval", "series-entire"),
        5: (
            "series-taylor",
            "series-maclaurin-sine",
            "series-maclaurin-cosine",
            "series-maclaurin-log",
        ),
    },
    "multivariable-functions": {
        1: (
            "multivariable-domain-two",
            "multivariable-domain-three",
            "multivariable-value-two",
            "multivariable-value-three",
        ),
        2: (
            "multivariable-gradient-two",
            "multivariable-directional",
            "multivariable-third-partial",
        ),
        3: (
            "multivariable-differential-two",
            "multivariable-differential-three",
            "multivariable-gradient-three",
        ),
        4: ("multivariable-local-minimum", "multivariable-classify"),
        5: ("multivariable-constrained", "multivariable-box"),
    },
    "differential-equations": {
        1: ("ode-separable-exponential", "ode-separable-root"),
        2: ("ode-linear", "ode-linear-variable"),
        3: ("ode-harmonic", "ode-distinct-roots"),
        4: ("ode-repeated-root", "ode-resonance"),
        5: ("ode-laplace-exponential", "ode-laplace-oscillator"),
    },
}
