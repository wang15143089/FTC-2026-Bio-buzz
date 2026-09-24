# Launcher and feeder engineering baseline

Status: CAD baseline complete; physical validation not recorded.  
Published to: [Notion — FTC Robot Project — 2026 biobuzz](https://app.notion.com/p/3e27fc7bbcfb81159c11c41464b523fc).  
Linear project: https://linear.app/keithschoolrobotic/project/ftc-2026-biobuzz-c4695fa110f5

## Subsystems and traceability

- Transfer System: KEI-5; CAD baseline KEI-7; prototype KEI-8; reliability/redesign KEI-11.
- Scoring Mechanism: KEI-6; CAD baseline KEI-9; component/rule verification KEI-10; spin test KEI-12; integrated accuracy KEI-13.
- Notion publication dependency: KEI-14.

## Current design

The current constrained concept combines a continuous three-paddle feeder with an adjustable opposed-flywheel launcher. The coordinate convention is X–Y on the chassis mounting plane, +Z upward, and +X along the horizontal projection of launch.

### Transfer geometry

- Three guide stages: 0°, 26°, and 52°; modeled lengths 70, 55, and 70 mm.
- Three replaceable flexible paddles; 96 mm width; 6 mm nominal side clearance.
- Constrained model sweep radius: 60 mm.
- Direct continuous-rotation servo drive.
- Modeled operating range: 25–40 rpm, or 1.25–2.0 objects/s theoretically.
- Channel clear section: 108 × 110 mm.

### Launcher geometry

- Four 96 × 24 mm Gecko wheels, two on each 8 mm shaft.
- POLLEN: 160 mm shaft spacing and 64 mm nominal wheel gap.
- NECTAR: 178 mm shaft spacing and 82 mm nominal wheel gap.
- Each shaft travels 9 mm; combined spacing change is 18 mm.
- 16 mm bearing-hole slots have 25 mm total outline length.
- Current launch axis: 52°; earlier design intent preserves a 42°–58° adjustment range.
- Symmetric adjustment linkage: 12 mm servo crank, 65 mm drive rod, horizontal slider, and two 110 mm links.
- Current constrained model envelope: approximately 383.8 × 410.0 × 400.0 mm, within 18 in in each axis.

## Decision record: constrained three-paddle feeder and adjustable opposed flywheels

Decision: Use the constrained three-paddle feeder integrated with two adjustable opposed-flywheel shafts as the current CAD baseline.

Reason: The layout removes conveyor belts, provides direct continuous feeding, retains separate POLLEN and NECTAR compression settings, keeps the shafts parallel through adjustment, and passes the recorded modeled interference checks.

Alternatives: An earlier horizontal/38° continuous-servo belt feeder with a 72 mm pinch roller; an earlier envelope-level horizontal feed with kick and guide rollers; unconstrained paddle/launcher concepts.

Evidence: `cad/README.md`, `cad/CONSTRAINED_PADDLE_LAUNCHER_README.md`, `cad/output/paddle_launcher_feasibility_report.md`, generated STEP/STL/GLB artifacts, and part exports under `cad/output/parts/`. The report records zero positional error at guide joints and successful modeled interference checks for both gap configurations.

Risks: Game-piece geometry and compliance are not represented; motors and servos are envelopes; wheel expansion, hub retention, bearing fits, shaft retention, chassis interfaces, target geometry, launch legality, vibration, current, heat, feed reliability, and accuracy are unverified. The 52° choice is based partly on a vacuum trajectory approximation and must not be treated as field calibration.

Next step: Complete KEI-10, then build and safely spin-test under KEI-12. In parallel, build the feeder prototype under KEI-8. Use the resulting evidence in KEI-11 and KEI-13; create redesign issues for any failed criterion.

## Test plan baseline

- Feeder: at least 100 cycles across representative samples and battery states; record success, jam, double-feed, rollback, damage, current, voltage, rpm, and feed rate.
- Launcher: staged low-to-high-speed guarded spin test; record rpm, current, temperature, vibration, deflection, rubbing, fastener movement, and gap-repeatability.
- Integrated scoring: at least 100 shots across intended distances, samples, battery states, angles, wheel speeds, and feed timings; report hit rate, dispersion, misfeeds, recovery, and thermal/electrical behavior.
- A failed test keeps the parent subsystem open and produces a redesign or follow-up issue.

## Sources in the repository

- `cad/README.md`
- `cad/CONSTRAINED_PADDLE_LAUNCHER_README.md`
- `cad/output/paddle_launcher_feasibility_report.md`
- `cad/output/paddle_launcher_constraint_report.md`
- `cad/output/continuous_servo_feeder_parameters.json`
- `cad/output/paddle_feeder_launcher_parameters.json`
- `cad/output/design_parameters.json`
