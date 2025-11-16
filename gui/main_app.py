from qtpy.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from qtpy.QtCore import Qt
import sys

from .map_widget import MapWidget
from .wells_table import WellsTable
from backend.aquifer_solver import estimate_aquifer_properties
from gui.drawdown_plot import DrawdownPlot

class GroundwaterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Unconfined Aquifer Analyzer – QtPy + Map")
        self.resize(1300, 800)

        # --- Center Map ---
        self.map_widget = MapWidget()

        # --- Table for pumping & observation wells ---
        self.table = WellsTable()

        # --- Buttons ---
        run_button = QPushButton("Run Aquifer Analysis")
        run_button.clicked.connect(self.run_analysis)

        layout = QVBoxLayout()
        layout.addWidget(self.map_widget, stretch=5)
        layout.addWidget(self.table, stretch=2)
        layout.addWidget(run_button, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect map clicks → table method
        self.map_widget.coordinates_clicked.connect(self.table.add_well_from_map)

    def run_analysis(self):
        wells = self.table.get_wells()
        if len(wells) < 2:
            print("Need at least 1 pumping well + 1 observation well")
            return

        results = estimate_aquifer_properties(wells)
        print("\n===== AQUIFER ANALYSIS RESULTS =====")
        print(results)


def run_app():
    app = QApplication(sys.argv)
    win = GroundwaterApp()
    win.show()
    sys.exit(app.exec())

self.plot_widget = DrawdownPlot()
layout.addWidget(self.plot_widget, stretch=3)

results = estimate_aquifer_properties(well, obs_list)

# Example: using backend functions
from backend.aquifer_solver import theis_drawdown, neuman_drawdown

r = distance(pumping_well, obs)
t = obs.t
s_obs = obs.s

# Use results from your solver
T_est = results["Obs Well 1 — Theis"]["T (ft²/day)"]
S_est = results["Obs Well 1 — Theis"]["S (dimensionless)"]

s_theis = theis_drawdown(r, t, pumping_well.Q, T_est, S_est)

# Neuman
Tn = results["Obs Well 1 — Neuman"]["T (ft²/day)"]
Sy = results["Obs Well 1 — Neuman"]["Sy"]
A = results["Obs Well 1 — Neuman"]["Vertical/Horizontal K ratio"]

s_neuman = neuman_drawdown(r, t, pumping_well.Q, Tn, Sy, A)

# Plot it
self.plot_widget.plot_drawdown(t, s_obs, s_theis=s_theis, s_neuman=s_neuman)
