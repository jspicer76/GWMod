class PumpingWell:
    def __init__(self, lat, lon, Q):
        self.lat = lat
        self.lon = lon
        self.Q = Q  # GPM or ft3/s etc.


class ObservationWell:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.drawdown_data = []  # future: store time–s pairs
