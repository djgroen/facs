"""Module for MPIManager class."""

import numpy as np

try:
    from mpi4py import MPI
except ImportError:
    print("MPI4Py module is not loaded, mode=parallel will not work.")


class MPIManager:
    def __init__(self):
        global log_prefix
        if not MPI.Is_initialized():
            print("Manual MPI_Init performed.")
            MPI.Init()
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

    def CalcCommWorldTotalSingle(self, i, op=MPI.SUM):
        in_array = np.array([i])
        total = np.array([-1.0])
        # If you want this number on rank 0, just use Reduce.
        self.comm.Allreduce([in_array, MPI.DOUBLE], [total, MPI.DOUBLE], op=MPI.SUM)
        return total[0]

    def CalcCommWorldTotalDouble(self, np_array):
        assert np_array.size > 0

        total = np.zeros(np_array.size, dtype="f8")

        # print(self.rank, type(total), type(np_array), total, np_array, np_array.size)
        # If you want this number on rank 0, just use Reduce.
        self.comm.Allreduce([np_array, MPI.DOUBLE], [total, MPI.DOUBLE], op=MPI.SUM)

        return total

    def CalcCommWorldTotal(self, np_array):
        assert np_array.size > 0

        total = np.zeros(np_array.size, dtype="int64")

        # print(self.rank, type(total), type(np_array), total, np_array, np_array.size)
        # If you want this number on rank 0, just use Reduce.
        self.comm.Allreduce([np_array, MPI.LONG], [total, MPI.LONG], op=MPI.SUM)

        return total

    def gather_stats(self, e, local_stats):
        e.global_stats = self.CalcCommWorldTotal(np.array(local_stats))
        # print(e.global_stats)
