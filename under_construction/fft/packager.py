import numpy as np
import pytest
from pyha import Hardware, simulate, sims_close, Complex


class DataWithIndex(Hardware):
    def __init__(self, data, index):
        self.data = data
        self.index = index

    @staticmethod
    def to2d(data):
        ret = []
        sublist = []
        for elem in data:
            if elem.index == 0:
                if len(sublist):
                    ret.append(sublist)
                sublist = [elem.data]
            else:
                sublist.append(elem.data)

        ret.append(sublist)
        return ret


class Packager(Hardware):
    def __init__(self, packet_size):
        self.PACKET_SIZE = packet_size
        self.counter = 0

        self.out = DataWithIndex(Complex(), 0)
        self.DELAY = 1

    def main(self, data):
        """
        :type data: Complex
        :rtype: DataWithIndex
        """

        self.out = DataWithIndex(data, index=self.counter)

        next_counter = self.counter + 1
        if next_counter >= self.PACKET_SIZE:
            next_counter = 0

        self.counter = next_counter

        return self.out

    def model_main(self, inp_list):
        out = np.array(inp_list).reshape((-1, self.PACKET_SIZE))
        return out


@pytest.mark.parametrize("M", [4, 8, 16, 32, 64, 128, 256])
def test_packager(M):
    dut = Packager(M)

    packets = np.random.randint(1, 4)
    inp = np.random.uniform(-1, 1, M * packets) + np.random.uniform(-1, 1, M * packets) * 1j

    sims = simulate(dut, inp, simulations=['MODEL', 'PYHA',
                                           # 'RTL'
                                           ])

    sims['PYHA'] = DataWithIndex.to2d(sims['PYHA'])
    assert sims_close(sims, rtol=1e-2)