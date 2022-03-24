#fmpy_test.py

import fmpy as fm
from fmpy.util import plot_result

fmu="FMUFile/MP_TestModel_for_linux.fmu"
fm.dump(fmu)

result=fm.simulate_fmu(fmu)
plot_result(result)
