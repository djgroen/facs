import numpy as np

class Disease():
  def __init__(self, infection_rate, incubation_period, mild_recovery_period, recovery_period, mortality_period, period_to_hospitalisation):
    self.infection_rate = infection_rate
    self.incubation_period = incubation_period
    self.mild_recovery_period = mild_recovery_period
    self.recovery_period = recovery_period
    self.mortality_period = mortality_period
    self.period_to_hospitalisation = period_to_hospitalisation
    self.hospital = np.zeros(91)
    self.mortality = np.zeros(91)


  def addHospitalisationChances(self, hosp_array):
    hosp_array = np.asarray(hosp_array)
    for a in range(0,len(self.hospital)):
      self.hospital[a] = np.interp(a, hosp_array[:,0], hosp_array[:,1])

  def addMortalityChances(self, mort_array):
    mort_array = np.asarray(mort_array)
    for a in range(0,len(self.mortality)):
      self.mortality[a] = np.interp(a, mort_array[:,0], mort_array[:,1])


  def print(self):
    print(self.infection_rate, self.incubation_period, self.mild_recovery_period, self.recovery_period, self.mortality_period)

