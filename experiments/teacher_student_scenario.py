from ..algos import ExpectationPropagation, StateEvolution, EarlyStopping
from ..algos.metrics import mean_squared_error, overlap
from ..models import DAGModel


class TeacherStudentScenario():
    """Implements teacher student scenario.

    Parameters
    ----------
    - model : DAGModel instance
        Generative model
    - x_ids : ids of the variables to infer (signals)
    - y_ids : ids of the observed variables (measurements)
    """

    def __init__(self, model, x_ids=["x"], y_ids=["y"]):
        if not isinstance(model, DAGModel):
            raise ValueError(f"{model} not a DAGModel")
        for x_id in x_ids:
            if x_id not in model.variable_ids:
                raise ValueError(f"x_id = {x_id} not in model variable_ids")
        for y_id in y_ids:
            if y_id not in model.variable_ids:
                raise ValueError(f"y_id = {y_id} not in  model variable_ids")
        self.x_ids = x_ids
        self.y_ids = y_ids
        self.teacher = model

    def setup(self):
        # teacher generate data
        sample = self.teacher.sample()
        self.true_values = sample
        self.x_true = {x_id: sample[x_id] for x_id in self.x_ids}
        self.observations = {y_id: sample[y_id] for y_id in self.y_ids}
        # pass it to the student
        self.student = self.teacher.to_observed(self.observations)

    def infer(self, max_iter=250, callback=None, initializer=None,
              check_decreasing=True):
        self.run_ep(
            max_iter=max_iter, callback=callback, initializer=initializer,
            check_decreasing=check_decreasing
        )
        self.run_se(
            max_iter=max_iter, callback=callback, initializer=initializer,
            check_decreasing=check_decreasing
        )

    def run_se(self, max_iter=250, callback=None, initializer=None,
               check_decreasing=True):
        callback = callback or EarlyStopping(tol=1e-6, min_variance=1e-12)
        se = StateEvolution(self.student)
        se.iterate(
            max_iter=250, callback=callback, initializer=initializer,
            check_decreasing=check_decreasing
        )
        se_x_data = se.get_variables_data(self.x_ids)
        self.mse_se = {x_id: data["v"] for x_id, data in se_x_data.items()}
        self.n_iter_se = se.n_iter

    def run_ep(self, max_iter=250, callback=None, initializer=None,
               check_decreasing=True):
        callback = callback or EarlyStopping(tol=1e-6, min_variance=1e-12)
        ep = ExpectationPropagation(self.student)
        ep.iterate(
            max_iter=250, callback=callback, initializer=initializer,
            check_decreasing=check_decreasing
        )
        ep_x_data = ep.get_variables_data(self.x_ids)
        self.x_pred = {x_id: data["r"] for x_id, data in ep_x_data.items()}
        self.mse_ep = {x_id: data["v"] for x_id, data in ep_x_data.items()}
        self.n_iter_ep = ep.n_iter
        # actual mse and overlap
        self.mse = {
            x_id: mean_squared_error(self.x_true[x_id], self.x_pred[x_id])
            for x_id in self.x_ids
        }
        self.overlap = {
            x_id: overlap(self.x_true[x_id], self.x_pred[x_id])
            for x_id in self.x_ids
        }
