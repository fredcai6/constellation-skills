## Wave review -- w4-mechanical

M2 and M3 merged; #555 carried unworked, its disposition still the human's.

**M1 is proven in production.** The two dispatches after it merged exported no SPINE_FILE in their scripts, and both bound their own door and claimed a derived, assignment-keyed identity with no attempt tail -- one of them a reviewer, the route where the identity used to be hand-typed.

**The wave's headline finding is a retraction.** Wave 4 recorded that binding a crew's door is necessary but not sufficient, because crews with bound doors still used the CLI. That basis does not hold: nine of this epic's ten dispatch scripts never set SPINE_FILE, so those crews had a door bound to a wave-1 scratch demo spine and the CLI was the only path to their own spine. They behaved correctly in a broken environment. Binding had been hand-typed per dispatch and was right once in ten -- which is the case for making it mechanical, stated as a measurement.

**Two rules were corrected by being broken.** A tracked config that code also reads directly must be launchable as committed, or a placeholder breaks every reader that runs before wiring. And omitting a tool from a crew's allow-list does not withhold the capability, because unrestricted Bash reaches the engine anyway -- found by the cold reviewer before N2 was dispatched rather than by a crew mid-flight.

**One Admiral error:** main was red and reported green. M3 deleted a documentation line that an approval file pins verbatim, and the suite was not re-run on merged main. Corrected in the same run; the M2 merge closed it, verified on merged main at 2522 passed.
