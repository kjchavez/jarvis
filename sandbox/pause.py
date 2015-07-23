"""
    @author: Kevin Chavez

    A rudimentary mechanism for detecting the end of an utterance. A more
    sophisticated approach might recognize that human speech exists in a
    particular frequency range, and check for power in that frequency range.

    TODO: Implement Fourier domain pause detector
"""
import numpy as np
from collections import deque


class PauseDetector(object):
    def __init__(self, rel_threshold=0.15, min_pause_length=15, smoothing=4):
        self.rel_threshold = rel_threshold
        self.min_pause_length = min_pause_length
        self.started = False
        self.quiet_count = 0
        self.max_energy = 0.01
        self.smoothing = smoothing
        self.energies = deque()

    def process(self, data, dtype=np.int16, debug=False):
        is_pause = False
        arr = np.fromstring(data, dtype=dtype)
        single_rms_energy = np.sqrt(np.sum(arr * arr)/arr.size)
        self.energies.append(single_rms_energy)

        if len(self.energies) < self.smoothing:
            return False

        self.energies.popleft()
        rms_energy = np.mean(self.energies)

        if not self.started:
            self.max_energy = rms_energy
            is_pause = False
            self.started = True
            return is_pause

        if rms_energy < self.rel_threshold * self.max_energy:
            self.quiet_count += 1
            if self.quiet_count > self.min_pause_length:
                is_pause = True
        else:
            is_pause = False
            self.quiet_count = 0
            if rms_energy > self.max_energy:
                self.max_energy = rms_energy

        if debug:
            print "Max Energy:", self.max_energy, "  Rel Energy:", rms_energy/self.max_energy
        return is_pause

    def reset(self):
        self.started = False
        self.quiet_count = 0
        self.max_energy = 0.01
