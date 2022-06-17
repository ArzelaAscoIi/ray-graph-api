from haystack import Pipeline
from haystack.nodes.retriever import TfidfRetriever
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes.retriever import BaseRetriever
from haystack.nodes.reader import BaseReader, FARMReader
from haystack.pipelines.base import read_pipeline_config_from_yaml, get_pipeline_definition, get_component_definitions
from pathlib import Path
from ray import serve
import ray
from ray.experimental.dag.input_node import InputNode
from ray.serve.drivers import DAGDriver
from ray.serve.http_adapters import json_request
from haystack import Document

ray.init(address="ray://ray:10001", namespace="default")
serve.start(detached=True)


config = read_pipeline_config_from_yaml(Path("pipeline2.yml"))
pipeline_definition = get_pipeline_definition(pipeline_config=config, pipeline_name="query")
component_definitions = get_component_definitions(
            pipeline_config=config,
        )

pipeline_definition
# pipeline = Pipeline.load_from_yaml(Path("pipeline.yml"), pipeline_name="query")
# pipeline

class MyRetriever(TfidfRetriever):
    def __init__(self,*args,**kwargs):
        document_store = InMemoryDocumentStore()
        document_store.write_documents([Document(content="Who the fuck is Arya?")])

        # kwargs["document_store"] = document_store
        super().__init__(*args, **kwargs, document_store=document_store)

ray_nodes = {}

for node in pipeline_definition["nodes"]:
    name = node["name"]
    # clazz = component_definitions[name]["type"]
    params = component_definitions[name].get("params") or {}
    # params["document_store"] = InMemoryDocumentStore()
    instantiated = Pipeline._load_or_get_component(name, component_definitions, components={})

    class MyRayComponent:
        wrapped = instantiated.__class__

        def __init__(self, *args, **kwargs) -> None:
            self._wrapped = self.wrapped(*args, **kwargs)

        def run(self, *args, **kwargs):
            # raise ValueError(args, kwargs)
            new_args = []
            for arg in args:
                if isinstance(arg, dict):
                    kwargs.update(arg)
                else:
                    new_args.append(arg)

            # TODO: args and kwargs in one dictionary
            output, stream_id = self._wrapped.run(*new_args, **kwargs)
            return output

    bound_clazz = serve.deployment(MyRayComponent).bind(**params)
    ray_nodes[name] = bound_clazz

results = {}

inputs_2 = []

with InputNode() as inp:
for node in pipeline_definition["nodes"]:
    input_names = node["inputs"]
        # Dict of name -> Ray run result
        inputs_2 += [results[input] if input != "Query" else inp[0] for input in input_names]
        
        inputs_3 = inputs_2.copy()
        if node["name"] == "Retriever":
            inputs_3.insert(0, input_names[0])

        result = ray_nodes[node["name"]].run.bind(*inputs_3,)
        results[node["name"]] = result

    # result = results["Retriever"]
    serve_dag = DAGDriver.bind(result, http_adapter=json_request)

dag_handle = serve.run(serve_dag)

print(ray.get(dag_handle.predict.remote([{"query": "who is Arya?"}])))

# for node, dependencies in pipeline.graph.succ:
#     instantiated_node = pipeline.components["node"]
#     # instantiated_node.
#     Wrapper(node)
