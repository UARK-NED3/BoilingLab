import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np

from scripts.run_single_case_demo import (
    add_event_markers,
    band_power_oscillation_spectrum,
    build_parser,
    characteristic_frequencies,
    default_output_dir,
    detect_dnb_time,
    detect_wall_temperature_peak_time,
    first_oscillation_peak_time,
    integrate_band_power,
    oscillation_envelope_growth,
    power_centroid_alignment,
    required_single_case_figure_paths,
    save_boiling_curve_plot,
    save_characteristic_frequency_analysis,
    save_hydrophone_analysis,
    save_wfs_ae_spectrogram,
    validate_required_single_case_figures,
)


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


class CharacteristicFrequencyTests(unittest.TestCase):
    def test_computes_peak_centroid_and_bandwidth(self):
        frequencies = np.array([100.0, 200.0, 300.0])
        psd = np.array(
            [
                [1.0, 0.0],
                [2.0, 1.0],
                [1.0, 3.0],
            ]
        )

        peak, centroid, bandwidth = characteristic_frequencies(
            frequencies,
            psd,
            band_min_hz=100.0,
            band_max_hz=300.0,
        )

        np.testing.assert_allclose(peak, [200.0, 300.0])
        np.testing.assert_allclose(centroid, [200.0, 275.0])
        np.testing.assert_allclose(bandwidth, [70.710678, 43.30127], rtol=1e-6)


class BoilingCurvePlotTests(unittest.TestCase):
    def test_saves_boiling_curve_plot(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "boiling_curve.png"

            save_boiling_curve_plot(
                path,
                time_s=np.array([0.0, 1.0, 2.0]),
                wall_temperature=np.array([90.0, 100.0, 110.0]),
                heat_flux=np.array([10.0, 25.0, 40.0]),
                off_time_s=1.5,
            )

            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 0)


class DnbDetectionTests(unittest.TestCase):
    def test_finds_maximum_before_sudden_heat_flux_drop(self):
        time = np.arange(0.0, 12.0, 1.0)
        heat_flux = np.array([0.0, 4.0, 8.0, 11.0, 12.0, 10.0, 3.0, 4.0, 6.0, 7.0, 8.0, 9.0])

        dnb_index, drop_start_index = detect_dnb_time(
            time,
            heat_flux,
            search_end_s=8.0,
            drop_window_s=1.0,
        )

        self.assertEqual(drop_start_index, 5)
        self.assertEqual(dnb_index, 4)

    def test_extracts_wall_temperature_peak_time(self):
        time = np.arange(0.0, 12.0, 1.0)
        wall_temperature = np.array(
            [80.0, 90.0, 110.0, 130.0, 160.0, 155.0, 140.0, 145.0, 150.0, 149.0, 148.0, 147.0]
        )

        peak_index = detect_wall_temperature_peak_time(
            time,
            wall_temperature,
            search_start_s=0.0,
            search_end_s=8.0,
        )

        self.assertEqual(peak_index, 4)


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


class OscillationEnvelopeGrowthTests(unittest.TestCase):
    def test_detects_growing_oscillation_envelope(self):
        time = np.arange(300.0, 700.0, 0.4)
        amplitude = 1.0 + 0.003 * (time - 300.0)
        signal = 20.0 + amplitude * np.sin(2 * np.pi * 0.08 * time)

        envelope, metrics = oscillation_envelope_growth(
            time,
            signal,
            window_start_s=300.0,
            window_end_s=700.0,
        )

        self.assertEqual(len(envelope), metrics["sample_count"])
        self.assertGreater(metrics["envelope_slope_per_s"], 0.0)
        self.assertGreater(metrics["envelope_fit_percent_change"], 50.0)

    def test_finds_first_peak_after_nominal_start(self):
        time = np.arange(295.0, 360.0, 0.1)
        signal = np.sin(2 * np.pi * 0.1 * (time - 302.5))

        peak_time = first_oscillation_peak_time(
            time,
            signal,
            search_start_s=300.0,
            search_end_s=360.0,
            baseline_window_s=20.0,
        )

        self.assertAlmostEqual(peak_time, 305.0, delta=0.5)


class PowerCentroidAlignmentTests(unittest.TestCase):
    def test_identifies_peak_to_peak_alignment(self):
        time = np.arange(300.0, 700.0, 0.4)
        power = np.sin(2 * np.pi * 0.08 * time)
        centroid = 1000.0 + 20.0 * np.sin(2 * np.pi * 0.08 * time)

        result = power_centroid_alignment(
            time,
            power,
            centroid,
            window_start_s=300.0,
            window_end_s=700.0,
        )

        self.assertGreater(result["zero_lag_correlation"], 0.95)
        self.assertGreater(result["mean_centroid_z_at_power_peaks"], 0.0)
        self.assertLess(result["mean_centroid_z_at_power_valleys"], 0.0)


class AcousticEventMarkerPlotTests(unittest.TestCase):
    def test_peak_event_label_is_on_right_side_of_marker(self):
        fig, ax = plt.subplots()
        try:
            ax.plot([0.0, 1.0], [0.0, 1.0])

            add_event_markers(ax, peak_time_s=0.5)

            peak_labels = [text for text in ax.texts if "peak" in text.get_text()]
            self.assertEqual(len(peak_labels), 1)
            self.assertEqual(peak_labels[0].get_ha(), "left")
        finally:
            plt.close(fig)

    def test_characteristic_frequency_plot_adds_event_markers(self):
        times = np.linspace(0.0, 4.0, 5)
        frequencies = np.array([0.0, 1000.0, 2000.0])
        psd = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [0.5, 0.5, 0.5, 0.5, 0.5],
            ]
        )

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            with patch("scripts.run_single_case_demo.add_event_markers") as markers:
                save_characteristic_frequency_analysis(
                    "unit",
                    times,
                    frequencies,
                    psd,
                    output_dir,
                    output_dir,
                    band_min_hz=0.0,
                    band_max_hz=2000.0,
                    color="tab:blue",
                    dnb_time_s=1.0,
                    peak_time_s=2.0,
                    off_time_s=3.0,
                )

        self.assertEqual(markers.call_count, 1)
        self.assertEqual(markers.call_args.kwargs["dnb_time_s"], 1.0)
        self.assertEqual(markers.call_args.kwargs["peak_time_s"], 2.0)
        self.assertEqual(markers.call_args.kwargs["off_time_s"], 3.0)

    def test_characteristic_frequency_plot_starts_x_axis_at_zero(self):
        times = np.linspace(0.5, 4.5, 5)
        frequencies = np.array([0.0, 1000.0, 2000.0])
        psd = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [0.5, 0.5, 0.5, 0.5, 0.5],
            ]
        )

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            with patch("matplotlib.axes.Axes.set_xlim") as set_xlim:
                save_characteristic_frequency_analysis(
                    "unit",
                    times,
                    frequencies,
                    psd,
                    output_dir,
                    output_dir,
                    band_min_hz=0.0,
                    band_max_hz=2000.0,
                    color="tab:blue",
                )

        set_xlim.assert_any_call(0, times[-1])


class SingleCaseOutputContractTests(unittest.TestCase):
    def test_default_output_dir_follows_test_id(self):
        self.assertEqual(default_output_dir("416"), Path("demos") / "Boiling-416" / "generated")
        self.assertEqual(
            default_output_dir("Boiling-417"),
            Path("demos") / "Boiling-417" / "generated",
        )

    def test_parser_includes_wfs_by_default_and_allows_skipping(self):
        parser = build_parser()

        self.assertTrue(parser.parse_args([]).include_wfs)
        self.assertFalse(parser.parse_args(["--skip-wfs"]).include_wfs)

    def test_required_figure_validation_rejects_missing_figures(self):
        with TemporaryDirectory() as tmpdir:
            plots_dir = Path(tmpdir)
            for path in required_single_case_figure_paths(plots_dir)[:-1]:
                path.write_text("placeholder", encoding="utf-8")

            with self.assertRaisesRegex(FileNotFoundError, "ae_wfs_characteristic_frequencies"):
                validate_required_single_case_figures(plots_dir)

    def test_missing_hydrophone_file_creates_required_placeholder_figures(self):
        with TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "case"
            plots_dir = Path(tmpdir) / "plots"
            case_dir.mkdir()
            plots_dir.mkdir()

            summary = save_hydrophone_analysis(
                case_dir,
                plots_dir,
                band_min_hz=0.0,
                band_max_hz=6000.0,
                oscillation_start_s=300.0,
                oscillation_end_s=700.0,
                oscillation_max_frequency_hz=0.2,
            )

            self.assertFalse(summary["hydrophone_available"])
            self.assertTrue((plots_dir / "hydrophone_spectrogram.png").exists())
            self.assertTrue((plots_dir / "hydrophone_band_integrated_power.png").exists())
            self.assertTrue((plots_dir / "hydrophone_characteristic_frequencies.png").exists())

    def test_missing_wfs_file_creates_required_placeholder_figures(self):
        with TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "case"
            plots_dir = Path(tmpdir) / "plots"
            case_dir.mkdir()
            plots_dir.mkdir()

            summary = save_wfs_ae_spectrogram(
                case_dir,
                plots_dir,
                channel=1,
                max_freq_hz=250000.0,
                band_min_hz=0.0,
                band_max_hz=250000.0,
                oscillation_start_s=300.0,
                oscillation_end_s=700.0,
                oscillation_max_frequency_hz=0.2,
                vmin_db=-180.0,
                vmax_db=-40.0,
            )

            self.assertFalse(summary["ae_wfs_available"])
            self.assertTrue((plots_dir / "ae_wfs_spectrogram.png").exists())
            self.assertTrue((plots_dir / "ae_wfs_band_integrated_power.png").exists())
            self.assertTrue((plots_dir / "ae_wfs_characteristic_frequencies.png").exists())


if __name__ == "__main__":
    unittest.main()
