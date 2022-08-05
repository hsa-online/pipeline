"""
NN inferencer

"""

import io
import numpy as np
import torch

from typing import List
from torch.autograd import Variable

from core.model import Model
from core.singleton import Singleton

class Inferencer(metaclass=Singleton):
    def __init__(self):
        self.__nn_model = Model(input_dim = 2, 
            output_dim = 1)

        self.__nn_id = ""

        # TODO: Remove debug output
        print('Inferencer created')

    @property
    def ready(self) -> str:
        return self.__nn_id != ""

    def load_weights(self, nn_id, data) -> bool:
        """
        Loads NN weights
        """

        buffer = io.BytesIO(data)

        self.__nn_model.load_state_dict(torch.load(buffer))
        self.__nn_model.eval()
        
        self.__nn_id = nn_id

        return True

    def predict(self, v: List) -> List:
        """
        Runs the NN to predict sum of the input vector's v components.
        """
        if not self.ready:
            res = []
            res.append(False)
            res.append('No weights loaded')
            res.append(0.0)

            return res

        x = torch.unsqueeze(torch.from_numpy(np.asarray(v)), 0)
        ds = torch.utils.data.TensorDataset(x)
        inference_loader = torch.utils.data.DataLoader(ds)

        with torch.no_grad():
            for inference in inference_loader:
                inference_batch = Variable(inference[0]).float()

                # Compute model output
                output_batch = self.__nn_model(inference_batch)

                predicted_by_nn = torch.squeeze(output_batch).numpy().astype(float)
                total = predicted_by_nn.tolist()

                res = []
                res.append(True)
                res.append(self.__nn_id)
                res.append(total)

                return res
