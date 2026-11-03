"""The approved #200 product matrix, independent of generator identity allocation."""

TOPIC_SPECS = (
    (
        "probability-events",
        "Events and counting",
        4,
        {
            1: ("events-equal",),
            2: (
                "events-complement",
                "events-at-least-one",
            ),
            3: (
                "events-union",
                "events-intersection",
            ),
            4: (
                "events-selection",
                "events-set",
            ),
            5: ("events-independence",),
        },
    ),
    (
        "conditional-probability",
        "Conditional probability and Bayes",
        5,
        {
            1: ("conditional-table",),
            2: (
                "conditional-replacement",
                "conditional-without",
            ),
            3: ("conditional-total",),
            4: ("conditional-bayes-two",),
            5: (
                "conditional-bayes-three",
                "conditional-tree",
            ),
        },
    ),
    (
        "discrete-random-variables",
        "Discrete random variables",
        5,
        {
            1: ("finite-normalize",),
            2: (
                "finite-point",
                "finite-cdf",
            ),
            3: (
                "finite-tail",
                "finite-support",
            ),
            4: ("finite-jump",),
            5: ("finite-transform",),
        },
    ),
    (
        "discrete-distributions",
        "Standard discrete distributions",
        5,
        {
            1: ("discrete-bernoulli",),
            2: ("discrete-binomial",),
            3: ("discrete-geometric",),
            4: ("discrete-hypergeometric",),
            5: ("discrete-poisson",),
        },
    ),
    (
        "continuous-distributions",
        "Continuous distributions",
        5,
        {
            1: ("continuous-uniform",),
            2: (
                "continuous-normalize",
                "continuous-support",
            ),
            3: (
                "continuous-piecewise-cdf",
                "continuous-interval",
            ),
            4: (
                "continuous-exponential-tail",
                "continuous-memoryless",
                "continuous-exponential-quantile",
            ),
            5: (
                "continuous-normal-standardize",
                "continuous-normal-probability",
                "continuous-normal-quantile",
            ),
        },
    ),
    (
        "moments-joint-distributions",
        "Moments and joint distributions",
        5,
        {
            1: ("moments-mean",),
            2: (
                "moments-variance",
                "moments-deviation",
            ),
            3: (
                "moments-affine-mean",
                "moments-affine-variance",
            ),
            4: (
                "moments-marginal",
                "moments-conditional",
            ),
            5: (
                "moments-covariance",
                "moments-correlation",
                "moments-independence",
            ),
        },
    ),
    (
        "descriptive-statistics",
        "Descriptive statistics",
        5,
        {
            1: (
                "sample-mean",
                "sample-weighted",
            ),
            2: (
                "sample-median",
                "sample-modes",
            ),
            3: (
                "sample-quartile",
                "sample-iqr",
            ),
            4: (
                "sample-population-variance",
                "sample-sample-variance",
                "sample-deviation",
            ),
            5: (
                "sample-correlation",
                "sample-slope",
                "sample-intercept",
            ),
        },
    ),
    (
        "confidence-intervals",
        "Confidence intervals",
        5,
        {
            1: ("ci-mean-z",),
            2: ("ci-mean-t",),
            3: (
                "ci-lower",
                "ci-upper",
            ),
            4: ("ci-proportion",),
            5: (
                "ci-paired",
                "ci-difference",
            ),
        },
    ),
    (
        "hypothesis-tests",
        "Hypothesis tests",
        5,
        {
            1: ("test-z-statistic",),
            2: ("test-z-decision",),
            3: (
                "test-t-statistic",
                "test-t-decision",
            ),
            4: ("test-proportion",),
            5: (
                "test-paired",
                "test-difference",
            ),
        },
    ),
)
