"""
NN inferencer: uses PyTorch, allows to load weights and to run the inference.

"""

import base64
import io
import numpy as np
import torch
import traceback


from torch.autograd import Variable
from typing import Any, List, Tuple

from core.model import Model
from core.singleton import Singleton

class Inferencer(metaclass=Singleton):
    def __init__(self):
        self.__nn_model = Model(input_dim = 2, 
            output_dim = 1)

        self.__nn_id = ""

    @property
    def ready(self) -> bool:
        return self.__nn_id != ""

    @property
    def nn_id(self) -> str:
        return self.__nn_id

    def load_weights(self, nn_id: str, data: Any) -> Tuple[bool, str]:
        """
        Loads NN weights. Also updates the NN identifier.
        """

        buffer = io.BytesIO(data)
        
        try:
            self.__nn_model.load_state_dict(torch.load(buffer))
        except RuntimeError:
            trace_str = traceback.format_exc()
            return (False, trace_str)

        self.__nn_model.eval()
        
        self.__nn_id = nn_id

        return (True, "")

    def predict(self, v: List) -> Tuple[bool, str, float]:
        """
        Runs the NN to predict sum of the input vector's v components.
        """

        if not self.ready:
            return (False, 'No weights loaded', 0.0)

        x = torch.unsqueeze(torch.from_numpy(np.asarray(v)), 0)
        ds = torch.utils.data.TensorDataset(x)
        inference_loader = torch.utils.data.DataLoader(ds)

        with torch.no_grad():
            for inference in inference_loader:
                inference_batch = Variable(inference[0]).float()

                try:
                    # Compute model output
                    output_batch = self.__nn_model(inference_batch)
                except RuntimeError:
                    # Can be caused for example by passing a wrong input 
                    trace_str = traceback.format_exc()
                    trace_str = base64.standard_b64encode(
                        trace_str.encode()).decode('utf-8')

                    return (False, trace_str, 0.0)

                predicted_by_nn = torch.squeeze(output_batch).numpy().astype(float)

                # Note: float is returned as the array consists of a single item only 
                total = predicted_by_nn.tolist() 

                return (True, self.__nn_id, total)
