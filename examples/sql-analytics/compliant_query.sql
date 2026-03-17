-- =============================================================
-- Compliant SQL Analytics — The Power of 15
-- =============================================================
-- Insurance attrition dashboard query following Rules 5-7, 9-10
--
-- Author: Pramod Misra
-- Target: Google BigQuery
-- Rules Reference: https://github.com/pramodmisra/power-of-15
-- =============================================================

-- Rule 10: No SELECT * — always specify columns explicitly
-- Rule 6: Use CTEs to contain scope (not temp tables where avoidable)
-- Rule 9: Flat, readable access — no deeply nested subqueries

-- CTE 1: Active policies with validated schema
WITH active_policies AS (
    SELECT
        p.policy_id,
        p.insured_name,
        p.line_of_business,
        p.written_premium,
        p.effective_date,
        p.expiration_date,
        p.producer_code,
        p.status_code
    FROM `project.dataset.policies` AS p
    WHERE p.status_code = 'Active'                       -- Rule 5: filter impossible states
      AND p.written_premium > 0                          -- Rule 5: business rule assertion
      AND p.effective_date IS NOT NULL                   -- Rule 5: null guard
      AND p.expiration_date > p.effective_date           -- Rule 5: logic assertion
),

-- CTE 2: Renewal outcomes — did the policy renew or lapse?
renewal_outcomes AS (
    SELECT
        ap.policy_id,
        ap.line_of_business,
        ap.written_premium,
        ap.producer_code,
        ap.expiration_date,
        CASE
            WHEN rn.policy_id IS NOT NULL THEN 'Renewed'
            ELSE 'Lapsed'
        END AS outcome
    FROM active_policies AS ap
    LEFT JOIN `project.dataset.policies` AS rn
        ON ap.policy_id = rn.prior_policy_id              -- Rule 9: single join, not nested
       AND rn.status_code IN ('Active', 'Pending')
),

-- CTE 3: Producer-level aggregation
producer_scorecard AS (
    SELECT
        ro.producer_code,
        COUNT(*) AS total_policies,
        COUNTIF(ro.outcome = 'Renewed') AS renewed_count,
        COUNTIF(ro.outcome = 'Lapsed') AS lapsed_count,
        ROUND(
            SAFE_DIVIDE(
                COUNTIF(ro.outcome = 'Renewed'),          -- Rule 7: SAFE_DIVIDE prevents /0
                COUNT(*)
            ) * 100, 2
        ) AS retention_rate_pct,
        ROUND(SUM(ro.written_premium), 2) AS total_premium,
        ROUND(
            SUM(CASE WHEN ro.outcome = 'Lapsed' THEN ro.written_premium ELSE 0 END),
            2
        ) AS lost_premium
    FROM renewal_outcomes AS ro
    GROUP BY ro.producer_code
)

-- Final output: producer scorecard with risk tier
SELECT
    ps.producer_code,
    ps.total_policies,
    ps.renewed_count,
    ps.lapsed_count,
    ps.retention_rate_pct,
    ps.total_premium,
    ps.lost_premium,
    CASE                                                  -- Rule 5: classify risk tiers
        WHEN ps.retention_rate_pct >= 90 THEN 'Low Risk'
        WHEN ps.retention_rate_pct >= 75 THEN 'Medium Risk'
        WHEN ps.retention_rate_pct >= 60 THEN 'High Risk'
        ELSE 'Critical'
    END AS risk_tier
FROM producer_scorecard AS ps
WHERE ps.total_policies >= 5                              -- Rule 5: minimum sample size
ORDER BY ps.lost_premium DESC
LIMIT 100                                                 -- Rule 3: always cap result sets
;
