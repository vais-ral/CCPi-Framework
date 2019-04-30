# -*- coding: utf-8 -*-
#   This work is part of the Core Imaging Library developed by
#   Visual Analytics and Imaging System Group of the Science Technology
#   Facilities Council, STFC

#   Copyright 2018-2019 Evangelos Papoutsellis and Edoardo Pasca

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from ccpi.framework import ImageData, ImageGeometry, AcquisitionGeometry, AcquisitionData

import numpy as np 
import numpy                          
import matplotlib.pyplot as plt

from ccpi.optimisation.algorithms import FISTA, CGLS

from ccpi.optimisation.operators import Gradient
from ccpi.optimisation.functions import ZeroFunction, L2NormSquared, FunctionOperatorComposition
from skimage.util import random_noise
from ccpi.astra.ops import AstraProjectorSimple
            
#%%

N = 75
x = np.zeros((N,N))
x[round(N/4):round(3*N/4),round(N/4):round(3*N/4)] = 0.5
x[round(N/8):round(7*N/8),round(3*N/8):round(5*N/8)] = 1

data = ImageData(x)
ig = ImageGeometry(voxel_num_x = N, voxel_num_y = N)

detectors = N
angles = np.linspace(0, np.pi, N, dtype=np.float32)

ag = AcquisitionGeometry('parallel','2D',angles, detectors)
Aop = AstraProjectorSimple(ig, ag, 'gpu')
sin = Aop.direct(data)

# Create noisy data. Apply Gaussian noise

np.random.seed(10)
noisy_data = sin + AcquisitionData(np.random.normal(0, 3, sin.shape))

# Regularisation Parameter

operator = Gradient(ig)

fidelity = FunctionOperatorComposition(L2NormSquared(b=noisy_data), Aop)
regularizer = ZeroFunction()

x_init = ig.allocate()

## Setup and run the FISTA algorithm
opt = {'tol': 1e-4, 'memopt':True}
fista = FISTA(x_init=x_init , f=fidelity, g=regularizer, opt=opt)
fista.max_iteration = 20
fista.update_objective_interval = 1
fista.run(20, verbose=True)

## Setup and run the CGLS algorithm        
cgls = CGLS(x_init=x_init, operator=Aop, data=noisy_data)
cgls.max_iteration = 20
cgls.run(20, verbose=True)

diff = np.abs(fista.get_output().as_array() - cgls.get_output().as_array())

plt.figure(figsize=(15,15))
plt.subplot(3,1,1)
plt.imshow(fista.get_output().as_array())
plt.title('FISTA reconstruction')
plt.colorbar()
plt.subplot(3,1,2)
plt.imshow(cgls.get_output().as_array())
plt.title('CGLS reconstruction')
plt.colorbar()
plt.subplot(3,1,3)
plt.imshow(diff)
plt.title('Difference reconstruction')
plt.colorbar()
plt.show()






























