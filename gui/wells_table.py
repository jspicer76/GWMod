from qtpy.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from qtpy.QtCore import Qt
from backend.models import PumpingWell, ObservationWell


class WellsTable(QWidget):
    def __init__(self):
        super().__init__()

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Type", "Latitude", "Longitude"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_well_from_map(self, well_type, lat, lon):
        row = self.table.rowCount()
        self.table.insertRow(row)

        if well_type == "pump":
            wtype = "Pumping Well"
        else:
            wtype = "Obs Well"

    self.table.setItem(row, 0, QTableWidgetItem(wtype))
    self.table.setItem(row, 1, QTableWidgetItem(str(lat)))
    self.table.setItem(row, 2, QTableWidgetItem(str(lon)))


    def get_wells(self):
        wells = []
        for i in range(self.table.rowCount()):
            wtype = self.table.item(i, 0).text()
            lat = float(self.table.item(i, 1).text())
            lon = float(self.table.item(i, 2).text())

            if wtype.lower().startswith("pump"):
                wells.append(PumpingWell(lat, lon, Q=500))  # default Q
            else:
                wells.append(ObservationWell(lat, lon))

        return wells
