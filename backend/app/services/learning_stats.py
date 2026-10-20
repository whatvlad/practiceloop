"""Private attempt-based constant-omission metrics.

Invalid expressions are excluded, and so are definite integrals (#36), whose
answers never take an integration constant.
"""

from typing import Any
from uuid import UUID

from psycopg import Connection


def metric(checked: int, omitted: int) -> dict[str, Any]:
    return {
        "checkedAttempts": checked,
        "omitted": omitted,
        "rate": omitted / checked if checked else None,
    }


def statistics(conn: Connection[Any], user_id: UUID) -> dict[str, Any]:
    rows = conn.execute(
        "select t.slug, p.difficulty, count(*), count(*) filter (where a.constant_omitted)"
        " from public.attempts a join public.problems p"
        " on p.id = a.problem_id and p.user_id = a.user_id"
        " join public.topics t on t.id = p.topic_id"
        " join private.problem_solutions s on s.problem_id = p.id"
        " where a.user_id = %s and a.is_correct is not null"
        " and s.generator_version <> 'definite-v1'"
        " group by t.slug, p.difficulty order by t.slug, p.difficulty",
        (user_id,),
    ).fetchall()
    weekly = conn.execute(
        "with weeks as (select generate_series("
        " date_trunc('week', now() at time zone 'UTC') - interval '7 weeks',"
        " date_trunc('week', now() at time zone 'UTC'), interval '1 week') as week),"
        " counts as (select date_trunc('week', created_at at time zone 'UTC') as week,"
        " count(*) as checked, count(*) filter (where a.constant_omitted) as omitted"
        " from public.attempts a join private.problem_solutions s on s.problem_id = a.problem_id"
        " where a.user_id = %s and a.is_correct is not null"
        " and s.generator_version <> 'definite-v1'"
        " and a.created_at >= date_trunc('week', now() at time zone 'UTC')"
        " at time zone 'UTC' - interval '7 weeks' group by 1)"
        " select w.week::date::text, coalesce(c.checked, 0), coalesce(c.omitted, 0)"
        " from weeks w left join counts c using (week) order by w.week",
        (user_id,),
    ).fetchall()
    return {
        **metric(sum(r[2] for r in rows), sum(r[3] for r in rows)),
        "byTopicDifficulty": [
            {"topic": r[0], "difficulty": r[1], **metric(r[2], r[3])} for r in rows
        ],
        "weekly": [{"week": r[0], **metric(r[1], r[2])} for r in weekly],
    }
