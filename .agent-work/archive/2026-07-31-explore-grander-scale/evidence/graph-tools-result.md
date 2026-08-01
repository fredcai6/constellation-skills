# Current Graph Tooling Research

Research date: 2026-07-29.

## Answer

Six maintained tools are credible, but they answer different questions.

- **Neo4j Community Edition is the best first experiment for learning how the network should be crawled.** It combines flexible property-graph writes, expressive bounded and shortest-path Cypher, official Python/JavaScript/.NET/Go/Java drivers, and an immediately useful visual query browser. Its cost is a local server and a GPLv3 Community Edition whose strongest schema constraints remain Enterprise-only.
- **LadybugDB is the most credible embedded property-graph experiment.** It is in-process, MIT-licensed, has Python/Node/Rust/Go/Swift/Java/C/C++ access, supports Cypher traversal and shortest paths, and now has an Explorer. It is newer and more schema-forward than Neo4j, so it should not yet be treated as a long-term commitment.
- **Oxigraph is the lightest credible semantic/RDF substrate.** It embeds cleanly in Rust or Python, also has JavaScript/WASM and a local server, uses standard RDF serializations and SPARQL, and gives named graphs as a natural provenance boundary. It has no documented bundled visual explorer or SHACL enforcement, and its own repository still characterizes query optimization as work in progress.
- **Apache Jena TDB2/Fuseki is the mature semantic option.** It adds SPARQL, named graphs, SHACL, inference/ontology facilities, text search, RDF Patch, standard exports, and both embedded-Java and local-server deployment. The price is the largest semantic and operational surface in the shortlist.
- **TypeDB is the strongest structured-reasoning option.** Relations are first-class, typed, n-ary, and can own provenance attributes; recursive functions can express reachability; schema violations fail at write/commit; Studio offers schema, data, and graph explorers. It is server-only, deliberately schema-first, and uses TypeQL rather than a standard graph language. That makes it promising for rigorous frames, but a poor first substrate for the globally loose network.
- **SQLite is the control.** A `node` table plus a first-class `edge/assertion` table provides the lowest operational burden, strongest portability, explicit provenance, full-text search, JSON metadata, and recursive traversal. It does not provide graph-native query ergonomics or visualization, so the application must supply both.

The important design inference is that **storage and crawling should be separate interfaces**. The store should preserve stable identities, typed connections, provenance, and portable export. A crawl service should impose depth/breadth bounds, relationship allow/deny lists, frame filters, cycle policy, and an explanation for every returned hop. Agents should call that service rather than receiving unrestricted database access as the permanent interface.

## Criteria

The comparison prioritizes:

1. Rapid creation of nodes and deliberately named connections without requiring a universal ontology.
2. Explainable crawling: bounded neighborhoods, direction/type filters, shortest paths, cycle handling, and retention of the actual traversed edges.
3. Local operation and straightforward agent access, especially from Python or HTTP.
4. Schema evolution that can begin loose and become strict inside selected frames.
5. First-class provenance and lifecycle metadata on connections.
6. A usable visual exploration path without making visualization the canonical store.
7. Portable, inspectable exports that prevent a tool experiment from becoming lock-in.

Fact/inference convention: tool capabilities and status below are sourced facts; each **Fit** statement is an inference for this project.

## Candidate comparison

### 1. Neo4j Community Edition — flexible property-graph reference

**Verified facts.** Neo4j CE is a GPLv3, single-instance property-graph server with ACID transactions, Cypher, Bolt, official drivers for Java, JavaScript, .NET, Go, and Python, and local installation through standalone packages, Desktop, or Docker. The current public repository is on the `2026.06` line. Neo4j Browser ships as the default developer interface and renders node/relationship query results as a graph. Cypher supports quantified path patterns, variable-length paths, shortest paths, path predicates, and current path modes. CE supports property uniqueness constraints, while property-existence, property-type, and key constraints are Enterprise features. ([editions and APIs](https://neo4j.com/docs/operations-manual/current/introduction/), [repository and license](https://github.com/neo4j/neo4j), [Browser](https://neo4j.com/docs/browser/), [path patterns](https://neo4j.com/docs/cypher-manual/current/patterns/variable-length-paths/), [constraints](https://neo4j.com/docs/cypher-manual/current/schema/constraints/), [Python driver](https://neo4j.com/docs/python-manual/current/install/))

**Schema/provenance.** Labels, relationship types, and properties can evolve without a predefined schema. An edge can carry `source_id`, `asserted_at`, `confidence`, `status`, and frame membership; an assertion that needs multiple participants or its own lifecycle can instead become a node. CE cannot fail fast on all required properties or types at the database layer, so those invariants need application validation.

**Crawling/visualization.** This is the strongest baseline for interactive traversal: Cypher returns actual paths, can constrain relationships and nodes inside repeated patterns, and Browser visualizes the result without a custom frontend. Unbounded or weakly filtered variable-length queries can still expand explosively; Neo4j's own documentation recommends finite bounds and inline predicates.

**Operations/APIs.** A JVM server must be installed or run in Docker/Desktop. Agents connect through a driver rather than embedding the store. This is more machinery than a file database but still modest for a single personal instance.

**Fit (inference).** Best first experiment because it minimizes time spent building query and visualization tooling and maximizes time spent learning which crawls and connection workflows are actually valuable. It is not the default recommendation for permanent canonical storage.

### 2. LadybugDB — embedded property graph

**Verified facts.** Ladybug is the maintained continuation of the database formerly named Kuzu. It is an MIT-licensed, in-process property graph with persistent and in-memory modes, serializable ACID transactions, Cypher, full-text and vector indexes, and official packages or bindings for Python, Node.js, Rust, Go, Swift, Java, C/C++, CLI, and WASM. Its documentation was updated in July 2026 and identifies `0.11.0` as the latest stable line. On-disk operation uses a WAL and checkpoints. ([documentation](https://docs.ladybugdb.com/), [repository and bindings](https://github.com/LadybugDB/ladybug), [installation](https://docs.ladybugdb.com/installation/), [persistence](https://docs.ladybugdb.com/get-started/))

Ladybug normally uses a structured property graph: node/relationship tables and typed properties are declared, and node tables require a primary key. It supports `ALTER TABLE`, including property and allowed-endpoint changes. Current releases also support open-type subgraphs for schema-looser compatibility. ([DDL](https://docs.ladybugdb.com/cypher/data-definition/), [ALTER](https://docs.ladybugdb.com/cypher/data-definition/alter))

**Schema/provenance.** Relationship properties support direct provenance, but a rapidly changing relationship vocabulary either causes relationship-table/schema growth or pushes the design toward a generic relationship table with a `kind` property. The latter weakens the main ergonomic advantage of typed Cypher edges. Open-type graphs may relieve this tension, but their behavior was not runtime-tested here.

**Crawling/visualization.** Ladybug supports bounded variable-length walks, filtered recursive relationships, named paths, shortest/all-shortest/weighted-shortest path syntax, and defaults an omitted maximum to 30 because its default traversal semantic permits repeated edges. Ladybug Explorer renders schema and query results as graph, table, or JSON and is distributed through Docker. ([recursive matching](https://docs.ladybugdb.com/cypher/query-clauses/match/), [Neo4j semantic differences](https://docs.ladybugdb.com/cypher/difference/), [Explorer](https://docs.ladybugdb.com/visualization/lbug-explorer/))

**Operations/APIs.** The database itself has no server process. Explorer is a separate component. Full database export produces Cypher schema/macros plus CSV or Parquet data, and query results export to CSV, Parquet, or JSON. Import currently requires an empty database and does not automatically roll back a failed import. ([migration/export](https://docs.ladybugdb.com/migrate/), [query export](https://docs.ladybugdb.com/export/))

**Fit (inference).** Best embedded candidate and likely the second experiment. Its low operational burden is attractive for an agent harness, but its youth, Kuzu lineage transition, and schema-vocabulary tension should be tested before durable adoption.

### 3. Oxigraph / pyoxigraph — lightweight embedded RDF

**Verified facts.** Oxigraph is a Rust/RocksDB RDF store, dual-licensed Apache-2.0/MIT. The official project offers a Rust library, `pyoxigraph`, JavaScript/WASM for Node, and a CLI/server implementing SPARQL 1.1 and Graph Store protocols. The repository listed release `0.5.7` in April 2026 and current pyoxigraph documentation is `0.5.9`; the repository describes the project as in heavy development and says SPARQL evaluation is not yet optimized. It implements SPARQL query/update/federation and standard RDF formats including Turtle, TriG, N-Triples, N-Quads, RDF/XML, and JSON-LD. ([repository, status, license, surfaces](https://github.com/oxigraph/oxigraph))

`pyoxigraph.Store` runs in-process, persists to a supplied directory or uses a temporary in-memory store, supports named graphs/quads, repeatable-read isolation, transactional loads/updates, backups, and standards-based dumps. ([pyoxigraph Store](https://pyoxigraph.readthedocs.io/en/stable/store.html))

**Schema/provenance.** RDF permits vocabulary growth without storage migrations. Named graphs can partition assertions by source, frame, or derivation run, while statement-level provenance can be represented through assertion resources/reification. Oxigraph itself does not document built-in SHACL validation or an inference engine; those would be application responsibilities or external components.

**Crawling/visualization.** SPARQL property paths provide concise reachability over sequences, alternatives, inverse edges, and repetitions. Standard property-path results bind endpoints rather than preserving each concrete route, so an explainable crawler should expand one frontier at a time or explicitly construct path records. The documented official Oxigraph package surface does not include a visual graph explorer.

**Operations/APIs.** Embedded Python/Rust is nearly as simple as SQLite; the CLI server provides a language-neutral HTTP seam. Standard N-Quads/TriG/JSON-LD dumps are the strongest native escape hatch in this shortlist.

**Fit (inference).** Best lightweight test of whether global identifiers, named graphs, and semantic interoperability are more valuable than path ergonomics. Less suitable as the first crawl experiment because route explanation and visualization must be built.

### 4. Apache Jena TDB2 + Fuseki — mature RDF/semantic stack

**Verified facts.** Apache Jena 6.1.0 is an actively released Apache-2.0 Java framework. TDB2 is its persistent, transactional, single-machine RDF store. Fuseki is a SPARQL 1.1 server that can run standalone, in Docker, as a service/webapp, or embedded in Java, and has a query UI. Jena 6 requires Java 21. ([release](https://jena.apache.org/download/), [repository/license](https://github.com/apache/jena), [TDB2](https://jena.apache.org/documentation/tdb2/), [Fuseki](https://jena.apache.org/documentation/fuseki2/))

Jena includes RDF APIs, SPARQL/Update, named datasets, RDFS/OWL-oriented inference facilities, SHACL and ShEx processors, Lucene text search, GeoSPARQL, RDF Patch, CLI tools, and standard RDF import/export. SHACL Core and SHACL SPARQL constraints can be invoked from the CLI/API and exposed as a Fuseki operation, but SHACL is not automatically enabled on every write. ([component overview](https://jena.apache.org/documentation/), [SHACL](https://jena.apache.org/documentation/shacl/))

**Schema/provenance.** This is the strongest RDF choice when evolving vocabulary, standards-based provenance, constraint shapes, and future semantic inference matter. Named graphs/quads map well to source or frame boundaries. SHACL shapes let a loose global graph coexist with strict local frames, though enforcement policy must be designed.

**Crawling/visualization.** ARQ implements SPARQL property paths and adds bounded `{n,m}` path lengths beyond standard SPARQL 1.1. As with Oxigraph, property paths answer reachability more naturally than concrete route narration. Fuseki's official UI is query-oriented; the current documentation does not advertise an integrated network explorer, so graph visualization remains external. ([ARQ property paths](https://jena.apache.org/documentation/query/property_paths.html))

**Operations/APIs.** Embedded use is Java-centric. Any language can use Fuseki over HTTP, at the cost of a Java server. TDB2 needs directory lifecycle, backup, and eventual compaction; only one JVM process may directly own a TDB2 directory, so multi-process access should go through Fuseki. ([TDB2 administration](https://jena.apache.org/documentation/tdb2/tdb2_admin.html))

**Fit (inference).** Best later semantic experiment if SHACL-defined frames, shared vocabularies, or inference become central. Too much machinery for the first crawl-learning loop.

### 5. TypeDB Community Edition — typed relations and explicit reasoning

**Verified facts.** TypeDB CE is an MPL-2.0 Rust server; the official repository listed release `3.10.4` on 2026-05-01. It runs locally on Windows/macOS/Linux or in Docker. Python, Rust, Java, C, C#, TypeScript/HTTP, a raw HTTP API, and an official Docker-distributed MCP server are documented. ([repository/status/license](https://github.com/typedb/typedb), [local install](https://typedb.com/docs/home/install/ce/), [drivers](https://typedb.com/docs/home/install/drivers/), [MCP server](https://typedb.com/docs/tools/mcp-server/))

TypeDB uses the polymorphic entity-relation-attribute model. Relations define named roles, may be n-ary, and relations themselves can own attributes. A schema must exist before data; ownership, role-playing, cardinality, value, and inheritance constraints are checked on writes and commits. Schema transactions support `define`, `undefine`, and single-change `redefine` operations. ([data model](https://typedb.com/docs/core-concepts/typeql/entities-relations-attributes/), [schema/data validation](https://typedb.com/docs/core-concepts/typeql/schema-data/), [schema evolution](https://typedb.com/docs/typeql-reference/schema/))

**Schema/provenance.** This is the cleanest direct model for a connection that is itself a rich object: an assertion relation can link claimant, proposition, source, frame, and evidence through named roles and own time/confidence/status attributes. The same strength creates upfront friction for spontaneous new node and relationship kinds.

**Crawling/visualization.** TypeQL matches typed relation patterns. Schema or query-scoped functions can be recursive, nested, and negated; the documented reachability example is tabled to break cycles and returns breadth-first. TypeDB 3 replaced implicit rules with explicitly called functions, so derived reasoning is no longer silently materialized. Studio provides query graph results, schema visualization, a data explorer, and an interactive graph explorer that can load adjacent relations on demand. ([recursive functions](https://typedb.com/docs/core-concepts/typeql/queries-as-functions/), [functions versus old rules](https://typedb.com/docs/typeql-reference/functions/functions-vs-rules/), [Studio](https://typedb.com/docs/tools/studio/))

**Operations/APIs.** A server, credentials, and driver/HTTP lifecycle are required. Self-hosted backups are the user's responsibility through disk snapshots or export/import. Export writes human-readable TypeQL schema plus proprietary binary data designed for cross-version TypeDB import; that is good product portability but weaker cross-database portability than RDF or normalized rows. ([export/import](https://typedb.com/docs/maintenance-operation/database-export-import/), [backups](https://typedb.com/docs/maintenance-operation/typedb-backups/))

**Fit (inference).** Strong candidate for rigorous subnetworks and explicit logical computation, not for the initial globally unstructured graph. It should be tested later with the same fixture to learn whether typed n-ary relations earn their authoring cost.

### 6. SQLite — minimal relational baseline

**Verified facts.** SQLite is public-domain, embedded, serverless, and stores a database in one cross-platform file with a stable format. Version `3.53.4` was released on 2026-07-24. Python ships a DB-API binding, current Node has `node:sqlite`, and SQLite publishes official browser WASM bindings. ([current release/license](https://sqlite.org/), [single-file guarantees](https://www.sqlite.org/onefile.html), [Python API](https://docs.python.org/3/library/sqlite3.html), [Node API](https://nodejs.org/api/sqlite.html), [WASM](https://www.sqlite.org/wasm/doc/trunk/index.md))

SQLite supports recursive CTEs for walking trees and graphs, foreign keys, `CHECK` constraints, per-table `STRICT` typing, JSON/JSONB functions, FTS5, transactions, and online backup. Foreign-key enforcement must be enabled for each connection. ([recursive CTEs](https://www.sqlite.org/lang_with.html), [foreign keys](https://www.sqlite.org/foreignkeys.html), [STRICT tables](https://www.sqlite.org/stricttables.html), [JSON](https://www.sqlite.org/json1.html), [FTS5](https://www.sqlite.org/fts5.html), [backup](https://www.sqlite.org/backup.html))

**Schema/provenance.** A normalized `nodes` table and first-class `edges` table make identity, source, assertion time, lifecycle, frame, confidence, and derivation explicit and constrainable. Additional specialized tables can enforce local frame rules. Schema migration is ordinary SQL and application code rather than graph vocabulary evolution.

**Crawling/visualization.** Recursive CTEs can retain the full path, depth, and visited-set state, which is excellent for explanation, but each traversal policy becomes verbose SQL. SQLite has no graph-native optimizer, path syntax, or integrated network explorer. The CLI can emit JSON/CSV, making external visualization straightforward but not turnkey. ([CLI output/export](https://www.sqlite.org/cli.html))

**Operations/APIs.** Lowest burden and easiest backup/inspection story. Concurrent personal-agent use must still respect SQLite's single-writer behavior and transaction boundaries.

**Fit (inference).** Best control experiment and a plausible durable kernel if graph traversals stay modest and all access is intentionally mediated. If the graph API is clean, SQLite could remain underneath without agents knowing; if crawl queries proliferate, it will expose the value of a graph-native engine quickly.

### Cross-candidate summary

| Candidate | Local shape | Crawl ergonomics | Schema evolution | Provenance affordance | Built-in visual path | Operational burden |
|---|---|---|---|---|---|---|
| Neo4j CE | Local server/Desktop/Docker | Excellent path-returning Cypher | Very loose; CE constraint ceiling | Edge properties or assertion nodes | Excellent: Browser | Medium |
| LadybugDB | Embedded file/in-memory | Excellent bounded/shortest Cypher | Typed tables plus `ALTER`; open graphs available | Edge properties or assertion nodes | Good: Explorer, separate Docker component | Low database / medium with Explorer |
| Oxigraph | Embedded Rust/Python, WASM, or HTTP server | Good reachability; weaker route narration | Vocabulary-flexible RDF; no documented built-in shapes | Excellent graph/source partition through quads | None documented | Low embedded |
| Jena TDB2/Fuseki | Embedded Java or local HTTP server | Good reachability; weaker route narration | Loose RDF plus optional SHACL/inference | Excellent quads/named graphs | Query UI, not documented as network explorer | Medium-high |
| TypeDB CE | Local server/Docker | Powerful typed patterns and recursive functions | Strict, explicit, fail-fast | Excellent n-ary attributed relations | Excellent: Studio | Medium |
| SQLite | Embedded single file | Fully controllable but verbose recursive SQL | Explicit migrations; strict tables optional | Excellent explicit assertion rows | None; export required | Very low |

## Exclusions

- **Kuzu was excluded despite being an obvious embedded candidate because its official repository was archived read-only on 2025-10-10.** LadybugDB is the maintained project now carrying that code lineage. ([archived Kuzu repository](https://github.com/kuzudb/kuzu), [Ladybug repository](https://github.com/LadybugDB/ladybug))
- **Obsidian, Logseq, and similar Markdown-first note applications were excluded as canonical stores.** They may remain excellent editors or projections, but do not provide the transactional, constraint, traversal, and agent API substrate being compared.
- **Graphology, NetworkX, Cytoscape.js, D3, and Graphviz were excluded as stores.** They are useful in-memory analysis or visualization layers and can consume any candidate's read model, but they do not solve durable local storage and multi-session mutation.
- **FalkorDB, Memgraph, ArangoDB, TerminusDB, GraphDB, Stardog, DuckPGQ, and other credible systems were not rejected.** They were not investigated deeply after the six-candidate stop condition because they add another server, license surface, or implementation variant without adding a model family missing from this comparison. A later excursion should revisit one only when a concrete missing capability selects it.

## Recommended first experiment

Run a **disposable Neo4j Community Edition crawl experiment**, not a migration.

Use a small, deliberately mixed fixture—roughly 50–150 nodes—from the existing architecture map, journal-system concepts, and one philosophical inquiry. Keep the fixture in a database-neutral JSONL or tabular form outside the database so the database can be discarded. Represent at least:

- concepts, claims, questions, artifacts/code, sources, and frames;
- deliberately declared and agent-inferred edges;
- one connection promoted, disputed, and retired;
- one node participating in several frames;
- edge provenance and confidence.

Expose five stable operations to both Fred and agents:

1. `connect(source, relation, target, provenance, status)` with fail-fast identity checks;
2. `neighborhood(start, depth, relation_filter, frame_filter, budget)`;
3. `paths_between(a, b, max_depth, relation_filter)`;
4. `explain_path(path_id)` returning every edge, provenance, and inclusion reason;
5. `suggest_connections(node, budget)` writing candidates into a quarantined status rather than declared truth.

Use Neo4j Browser to inspect the same returned subgraphs. Do not evaluate success by bulk performance. Evaluate:

- how quickly a useful connection can be created while thinking;
- whether a crawl returns a legible subgraph instead of a hairball;
- whether agents can explain why each hop is present;
- which filters repeatedly matter (frame, relation type, epistemic status, time, confidence, source);
- whether edge-as-record versus assertion-as-node feels natural;
- whether server lifecycle is actually annoying in daily personal use.

Then load the exact same fixture and operation contract into **one contrasting backend**, selected by the learned pain:

- choose Ladybug if server lifecycle is the main problem;
- choose TypeDB if semantic invalidity and rich n-ary relations are the main problem;
- choose Jena or Oxigraph if shared vocabularies, named-graph provenance, or semantic interoperability dominate;
- choose SQLite if the graph-native features were pleasant but not essential.

This sequence tests user interaction and crawl semantics before storage ideology.

## Migration/escape hatch

Do not let any candidate's internal identifiers or binary backup become the only durable representation.

Maintain a database-neutral logical export with:

- `nodes`: stable application ID, kind(s), human label, content/artifact reference, created/updated time, lifecycle, and extensible metadata;
- `edges`: stable application ID, source ID, target ID, named relation, direction, frame(s), provenance/source ID, author/agent, asserted time, confidence, epistemic status, lifecycle, and extensible metadata;
- `sources/events`: immutable source identity and content hash or artifact location;
- `frames`: stable identity plus optional schema/protocol version;
- vocabulary manifests: relation/node-kind definitions, aliases, and deprecations.

Use JSONL for inspectability and streaming, plus CSV/Parquet or N-Quads where the backend supports them. Never expose backend-generated node IDs as durable IDs. Keep traversal/query templates in the adapter layer and test their semantic results against a shared fixture. Before changing backends, export, recreate in a fresh store, and compare node IDs, edge IDs, counts, provenance fields, and the outputs of the five core operations.

Backend-native escape paths are strongest for RDF (N-Quads/TriG/JSON-LD), SQLite (stable single file plus SQL/CSV/JSON), and Ladybug (Cypher schema plus Parquet/CSV). Neo4j and TypeDB have reliable product-native backup/import, but cross-product movement still requires the logical export.

## Tested / NOT tested

**Tested:** current official documentation and official repositories available on 2026-07-29; maintenance/release signals; licenses; data and query models; local/embedded deployment forms; documented language/API surfaces; schema and constraint facilities; provenance-relevant primitives; path/reachability features; documented visualization surfaces; backup/export mechanisms. The six candidates were compared against the stated personal, local-first, agent-shared use case.

**NOT tested:** no software was installed; no databases or fixtures were created; no query was executed; no performance, memory, crash recovery, concurrency, Windows packaging, backup restore, import/export fidelity, schema migration, visualization usability, or agent integration was runtime-verified. No claim is made that documentation completeness proves absence of an undocumented feature. Enterprise/cloud-only capabilities and pricing were not evaluated except where edition boundaries affect the free local option. The private journal vault was not accessed. Recommendations are design inferences, not benchmark results.

## Sources

Primary sources only:

- Neo4j: [operations/editions](https://neo4j.com/docs/operations-manual/current/introduction/), [Cypher paths](https://neo4j.com/docs/cypher-manual/current/patterns/variable-length-paths/), [constraints](https://neo4j.com/docs/cypher-manual/current/schema/constraints/), [Browser](https://neo4j.com/docs/browser/), [Python driver](https://neo4j.com/docs/python-manual/current/install/), [repository/license](https://github.com/neo4j/neo4j).
- LadybugDB: [documentation](https://docs.ladybugdb.com/), [repository/license/bindings](https://github.com/LadybugDB/ladybug), [persistence and schema](https://docs.ladybugdb.com/get-started/), [DDL](https://docs.ladybugdb.com/cypher/data-definition/), [recursive traversal](https://docs.ladybugdb.com/cypher/query-clauses/match/), [Explorer](https://docs.ladybugdb.com/visualization/lbug-explorer/), [migration/export](https://docs.ladybugdb.com/migrate/).
- Oxigraph: [repository/status/license/surfaces](https://github.com/oxigraph/oxigraph), [pyoxigraph Store](https://pyoxigraph.readthedocs.io/en/stable/store.html).
- Apache Jena: [release](https://jena.apache.org/download/), [repository/license](https://github.com/apache/jena), [component overview](https://jena.apache.org/documentation/), [TDB2](https://jena.apache.org/documentation/tdb2/), [Fuseki](https://jena.apache.org/documentation/fuseki2/), [SHACL](https://jena.apache.org/documentation/shacl/), [ARQ property paths](https://jena.apache.org/documentation/query/property_paths.html), [TDB2 administration](https://jena.apache.org/documentation/tdb2/tdb2_admin.html).
- TypeDB: [repository/status/license](https://github.com/typedb/typedb), [local CE installation](https://typedb.com/docs/home/install/ce/), [data model](https://typedb.com/docs/core-concepts/typeql/entities-relations-attributes/), [schema/data validation](https://typedb.com/docs/core-concepts/typeql/schema-data/), [recursive functions](https://typedb.com/docs/core-concepts/typeql/queries-as-functions/), [Studio](https://typedb.com/docs/tools/studio/), [drivers](https://typedb.com/docs/home/install/drivers/), [MCP server](https://typedb.com/docs/tools/mcp-server/), [export/import](https://typedb.com/docs/maintenance-operation/database-export-import/).
- SQLite: [current release/license](https://sqlite.org/), [single-file format](https://www.sqlite.org/onefile.html), [recursive CTEs](https://www.sqlite.org/lang_with.html), [foreign keys](https://www.sqlite.org/foreignkeys.html), [STRICT tables](https://www.sqlite.org/stricttables.html), [JSON](https://www.sqlite.org/json1.html), [FTS5](https://www.sqlite.org/fts5.html), [backup](https://www.sqlite.org/backup.html), [CLI/export](https://www.sqlite.org/cli.html), [Python API](https://docs.python.org/3/library/sqlite3.html), [Node API](https://nodejs.org/api/sqlite.html), [official WASM](https://www.sqlite.org/wasm/doc/trunk/index.md).
- Explicit exclusion: [archived Kuzu repository](https://github.com/kuzudb/kuzu).
