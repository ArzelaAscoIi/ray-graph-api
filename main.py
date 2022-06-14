import ray
from ray import serve
from ray.experimental.dag.input_node import InputNode
from ray.serve.drivers import DAGDriver


ray.init(address="ray://ray:10001", namespace="default")
serve.start(detached=True)


@serve.deployment
class MyModel:
    def __init__(self):
        self.counter = 1

    def __call__(self, request):
        self.counter += 1
        return self.counter


# after
@serve.deployment
def combine(*args):
    return sum(args)


M1 = MyModel.bind("my_path")
M2 = MyModel.bind("my_path")
# with InputNode() as inp:
#    dag = combine.bind(M1.__call__.bind(inp), M2.__call__.bind(inp))
# serve.run(DAGDriver.bind(dag))

combine.deploy()
MyModel.deploy()
