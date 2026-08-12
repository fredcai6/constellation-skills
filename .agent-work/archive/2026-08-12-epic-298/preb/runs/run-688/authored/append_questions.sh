#!/bin/sh
# Append the interrogation question set through the engine (never hand-edit the survey).
set -e
ENGINE="C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py"
FILE=".agent-work/issue-688/interrogation.json"
S="intg-688"

run() { py "$ENGINE" --file "$FILE" append "$1" --session-id "$S" --title "$2" --imperative "$3" | tail -1; }

run q2 "[fact] What wet signals exist in the canonical DB, and what is each one's real coverage?" \
  "Enumerate every stored wet signal (sessions.rainfall blob, weather.rainfall per-sample, session_surface_features.session_rain_flag / wet_lap_count / wet_lap_fraction, lap_times.compound) and MEASURE coverage per season and session_type. Record evidence."

run q3 "[fact] Does this repo already have a precedented graded wet-exclusion seam?" \
  "Search for an existing named wet threshold plus stored-fraction read in physics. Record the seam, its threshold constant, and whether the architecture map sanctions the physics-to-data read."

run q4 "[fact] On real 2022-2024 data, does the issue's proposed fraction-of-wet-SAMPLES threshold actually discriminate a brief shower from genuinely wet running?" \
  "Compute per timed session the wet-weather-sample fraction and the WET/INTERMEDIATE lap fraction; look for sessions where the two disagree. Record counterexamples."

run q5 "[fact] Does the grip fit ingest wet laps at all -- what is actually at risk from a wet session?" \
  "Read _read_clean_session_laps compound filter and _wear_corrected_pace. Determine whether the risk is wet laps entering the fit, or dry laps sitting on a DRYING track."

run q6 "[DECISION] Which severity criterion do we adopt: weather-sample fraction, WET/INTERMEDIATE lap fraction, or a composite with an explicit unknown state?" \
  "Recommend, then take to the counterpart. Never self-answer without recorded authority."

run q7 "[DECISION] Does the fix REPLACE the binary rain_flag, or add a graded field alongside it (record and stored-DB compatibility)?" \
  "Weigh the GripEstimateRecord additive-migration contract and every existing rain_flag reader. Recommend, then take to the counterpart."

run q8 "[DECISION] Does the flat RAIN_SIGMA_INFLATION=4.0 become graded in severity, or stay flat with only the SELECTION criterion loosened?" \
  "The issue asks only about exclusion, but a flat 4x on a zero-wet-lap session is the same over-aggression in sigma form. Recommend, then take to the counterpart."

run q9 "[DECISION] Does issue 688 own the data-layer coverage extension (populating wet_lap_fraction for non-race sessions), or is that a separate issue?" \
  "The grip fit runs over every session type but the wet-fraction seam is populated for races only. Without the extension the loosened rule has no signal to read for Q/SQ/S/FP. Recommend, then take to the counterpart."

run q10 "[DECISION] Where does the usable-for-pooling SELECTION predicate live so consumers stop reinventing it per-spike?" \
  "The 20-of-36 drop happened in a consumer, not the producer. Decide whether this issue ships a named production predicate or only the graded severity field. Recommend, then take to the counterpart."

run q11 "[fact] What regeneration or re-batch does the change imply, and what does it cost?" \
  "Determine whether the grip store must be re-run with --force, whether the season DBs need a wet-feature repopulate, and how expensive each is."

run q12 "[fact] What guards the conservative direction -- what evidence proves genuinely wet running is still excluded?" \
  "Identify the known-wet sessions in 2022-2024 that any accepted rule MUST still exclude, and the known-dry-despite-a-shower sessions it MUST recover. These become frozen test cases."
