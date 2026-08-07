"""Read-only weekend-grain sizing probe for #688 planning (no repo mutation).

Tests the plan-shaping hypothesis: is the ~55% weekend drop driven by
per-session OVER-FLAGGING (a stray wet sample in an otherwise dry session), or
by WEEKEND-GRAIN AGGREGATION (one genuinely-wet session condemning its four
dry siblings)?
"""
import sqlite3

WET = ("INTERMEDIATE", "WET")

for year in (2022, 2023):
    con = sqlite3.connect(f"file:data/f1_data_{year}.db?mode=ro", uri=True)
    rows = con.execute(
        """
      SELECT s.gp_name, s.session_type,
             COALESCE(f.session_rain_flag, 0),
             SUM(CASE WHEN l.compound IN ('INTERMEDIATE','WET') THEN 1 ELSE 0 END)*1.0
               / NULLIF(COUNT(l.session_id), 0)
      FROM sessions s
      LEFT JOIN lap_times l ON l.session_id = s.id
      LEFT JOIN session_surface_features f ON f.session_id = s.id
      GROUP BY s.id ORDER BY s.gp_name, s.session_type
    """
    ).fetchall()
    con.close()

    weekends: dict[str, list] = {}
    for gp, st, flag, wf in rows:
        weekends.setdefault(gp, []).append((st, int(flag), wf))

    n_wk = len(weekends)
    any_flag = sum(1 for v in weekends.values() if any(f for _, f, _ in v))
    # sessions surviving under each rule
    tot_sess = sum(len(v) for v in weekends.values())
    surv_weekend_rule = sum(
        len(v) for v in weekends.values() if not any(f for _, f, _ in v)
    )
    surv_session_binary = sum(1 for v in weekends.values() for _, f, _ in v if not f)
    surv_session_graded = sum(
        1
        for v in weekends.values()
        for _, f, wf in v
        if not f or (wf is not None and wf < 0.05)
    )
    print(f"=== {year} ===")
    print(f"  weekends={n_wk}  any-session-flagged weekends={any_flag} "
          f"({any_flag / n_wk:.0%})")
    print(f"  sessions total={tot_sess}")
    print(f"    survive ANY-SESSION-WET weekend rule : {surv_weekend_rule}"
          f" ({surv_weekend_rule / tot_sess:.0%})")
    print(f"    survive per-session binary flag      : {surv_session_binary}"
          f" ({surv_session_binary / tot_sess:.0%})")
    print(f"    survive per-session graded (<5% wet) : {surv_session_graded}"
          f" ({surv_session_graded / tot_sess:.0%})")
