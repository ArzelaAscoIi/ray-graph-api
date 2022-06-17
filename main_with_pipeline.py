from haystack import Pipeline
from haystack.pipelines.base import read_pipeline_config_from_yaml, get_pipeline_definition, get_component_definitions
from pathlib import Path
from ray import serve
import ray
from ray.experimental.dag.input_node import InputNode
from ray.serve.drivers import DAGDriver
from ray.serve.http_adapters import json_request

ray.init(address="ray://ray:10001", namespace="default")
serve.start(detached=True)


config = read_pipeline_config_from_yaml(Path("pipeline.yml"))
pipeline_definition = get_pipeline_definition(pipeline_config=config, pipeline_name="query")
component_definitions = get_component_definitions(
            pipeline_config=config,
        )

pipeline_definition
# pipeline = Pipeline.load_from_yaml(Path("pipeline.yml"), pipeline_name="query")
# pipeline

# @serve.deployment()
class Wrapper:

    def __init__(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass

ray_nodes = {}

for node in pipeline_definition["nodes"]:
    name = node["name"]
    # clazz = component_definitions[name]["type"]
    params = component_definitions[name].get("params") or {}
    # params["document_store"] = InMemoryDocumentStore()
    instantiated = Pipeline._load_or_get_component(name, component_definitions, components={})

    bound_clazz = serve.deployment(instantiated.__class__).bind(**params)
    ray_nodes[name] = bound_clazz

with InputNode() as inp:
for node in pipeline_definition["nodes"]:
    input_names = node["inputs"]
        # Dict of name -> Ray run result
        inputs_2 = {input: ray_nodes[input].run.bind() if input != "Query" else inp[0] for input in input_names}
        result = ray_nodes[node["name"]].run.bind(**inputs_2)

    serve_dag = DAGDriver.bind(result, http_adapter=json_request)

dag_handle = serve.run(serve_dag)

print(ray.get(dag_handle.predict.remote([{"query": "who is Arya?"}])))

# for node, dependencies in pipeline.graph.succ:
#     instantiated_node = pipeline.components["node"]
#     # instantiated_node.
#     Wrapper(node)

    