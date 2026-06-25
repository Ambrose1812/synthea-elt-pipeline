# Airflow DAG: orchestration notes

## The test_behavior bug

My first DAG run failed with `relation "analytics.high_utilizers" does not exist`,
which was confusing since `dbt run` had already built that model fine outside
of Airflow. Used AI to figure out what was going on to be honest..

Turns out it's a Cosmos default I didn't know about. Cosmos runs tests right
after each model builds (`test_behavior="after_each"`). The problem is that
dbt relationship tests get attached to both models they're comparing, not
just one. So a test checking that `high_utilizers.patient_id` shows up in
`stg_patients.patient_id` actually gets tied to `stg_patients` as well.

That meant the moment Cosmos finished building `stg_patients` and went to
test it, dbt pulled in every test connected to that model, including ones
that needed `high_utilizers` and `patient_encounter_summary` to already
exist. Those models hadn't run yet since they come later in the DAG, so the
tests failed for a reason that had nothing to do with `stg_patients` itself.
Everything downstream then got marked "Upstream Failed," which looked like
a bigger problem than it actually was.

Once I found it: set `test_behavior=TestBehavior.AFTER_ALL` on
the RenderConfig. Making Cosmos build every model first and only run the
full test suite once everything in the project actually exists.
