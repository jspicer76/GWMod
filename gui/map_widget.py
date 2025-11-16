import folium
import io

from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtCore import QObject, Signal, Slot, QUrl
from qtpy.QtWebChannel import QWebChannel


class MapBridge(QObject):
    """Bridge that receives JS map-click events."""
    observation_clicked = Signal(float, float)
    pumping_clicked = Signal(float, float)

    @Slot(float, float)
    def left_click(self, lat, lon):
        self.observation_clicked.emit(lat, lon)

    @Slot(float, float)
    def right_click(self, lat, lon):
        self.pumping_clicked.emit(lat, lon)


class MapWidget(QWebEngineView):
    def __init__(self):
        super().__init__()

        self.bridge = MapBridge()
        self.bridge.observation_clicked.connect(self.add_observation_marker)
        self.bridge.pumping_clicked.connect(self.add_pumping_marker)

        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.page().setWebChannel(self.channel)

        # base map
        self.map = folium.Map(location=[38.5, -85.7], zoom_start=8)

        self._inject_click_handlers()
        self.update_map()

    def _inject_click_handlers(self):
        """Adds JS to differentiate left and right click on map."""

        js = """
        function addBridgeHandlers(){
            document.map.on('click', function(e){
                bridge.left_click(e.latlng.lat, e.latlng.lng);
            });

            document.map.on('contextmenu', function(e){
                // right-click
                bridge.right_click(e.latlng.lat, e.latlng.lng);
            });
        }
        """

        # attach JS to folium map template
        self.map.get_root().script.add_child(folium.Element(js))

        # create placeholder for map object
        self.map.get_root().html.add_child(folium.Element(
            "<script>var map_init_function = function(){};</script>"
        ))

        # hook into folium's onLoad event
        self.map.get_root().html.add_child(folium.Element("""
            <script>
                document.addEventListener("DOMContentLoaded", function(){
                    // Leaflet stores map instance as window.L_MAP_INSTANCE in folium >= 0.14
                    document.map = window.L_MAP_INSTANCE;
                    addBridgeHandlers();
                });
            </script>
        """))

    def update_map(self):
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        html = data.getvalue().decode()
        self.setHtml(html)

    # ---------- Marker drawing ----------
    def add_observation_marker(self, lat, lon):
        folium.Marker([lat, lon], popup="Obs Well", icon=folium.Icon(color="blue")).add_to(self.map)
        self.update_map()
        self.parent().coordinates_clicked.emit("obs", lat, lon)

    def add_pumping_marker(self, lat, lon):
        folium.Marker([lat, lon], popup="Pumping Well", icon=folium.Icon(color="red")).add_to(self.map)
        self.update_map()
        self.parent().coordinates_clicked.emit("pump", lat, lon)
