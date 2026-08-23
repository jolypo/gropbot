import numpy as np
class ProbabilityCalibrator:
 def __init__(self,min_samples=100):self.min_samples=min_samples;self._prob=None
 def fit(self,outcomes):
  x=np.asarray(outcomes,dtype=float)
  if len(x)<self.min_samples:self._prob=None;return None
  self._prob=float((x.sum()+1)/(len(x)+2)*100);return self._prob
 @property
 def probability(self):return self._prob
