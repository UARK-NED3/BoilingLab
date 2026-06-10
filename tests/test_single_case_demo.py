import unittest

import numpy as np

from scripts.run_single_case_demo import band_power_oscillation_spectrum, integrate_band_power


class IntegratedBandPowerTests(unittest.TestCase):
    def test_integrates_psd_over_frequency_band(self):
        frequencies = np.array([0.0, 10.0, 20.0, 30.0])
        times = np.array([1.0, 2.0])
        psd = np.array(
            [
                [0.0, 0.0],
                [1.0, 2.0],
                [3.0, 6.0],
                [5.0, 10.0],
            ]
        )

        integrated, integrated_db = integrate_band_power(
            frequencies,
            times,
            psd,
            band_min_hz=10.0,
            band_max_hz=30.0,
        )

        np.testing.assert_allclose(integrated, [60.0, 120.0])
        np.testing.assert_allclose(integrated_db, 10 * np.log10([60.0, 120.0]))

    def test_rejects_empty_frequency_band(self):
        frequencies = np.array([100.0, 200.0])
        times = np.array([1.0])
        psd = np.ones((2, 1))

        with self.assertRaisesRegex(ValueError, "No PSD frequency bins"):
            integrate_band_power(
                frequencies,
                times,
                psd,
                band_min_hz=300.0,
                band_max_hz=400.0,
            )


class BandPowerOscillationTests(unittest.TestCase):
    def test_detects_dominant_low_frequency_modulation(self):
        time = np.arange(300.0, 700.0, 0.4)
        power = 2.0 * np.sin(2 * np.pi * 0.08 * time)

        _, _, dominant_frequency, dominant_period, n_samples = band_power_oscillation_spectrum(
            time,
            power,
            window_start_s=300.0,
            window_end_s=700.0,
            max_frequency_hz=0.2,
        )

        self.assertEqual(n_samples, len(time))
        self.assertAlmostEqual(dominant_frequency, 0.08, places=2)
        self.assertAlmostEqual(dominant_period, 12.5, places=1)


if __name__ == "__main__":
    unittest.main()
