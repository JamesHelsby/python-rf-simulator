import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(element):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_simulation_xml(rows, cols, layers, spacing_x, spacing_y, spacing_z, tx_range, interference_range, success_ratio_tx, success_ratio_rx):
    simconf = ET.Element("simconf", version="2023090101")
    simulation = ET.SubElement(simconf, "simulation")
    
    ET.SubElement(simulation, "title").text = f"java_{rows}x{cols}x{layers}"
    ET.SubElement(simulation, "randomseed").text = "generated"
    ET.SubElement(simulation, "motedelay_us").text = "1000000"
    
    radiomedium = ET.SubElement(simulation, "radiomedium")
    radiomedium.text = "org.contikios.cooja.radiomediums.UDGM"
    ET.SubElement(radiomedium, "transmitting_range").text = str(tx_range)
    ET.SubElement(radiomedium, "interference_range").text = str(interference_range)
    ET.SubElement(radiomedium, "success_ratio_tx").text = str(success_ratio_tx)
    ET.SubElement(radiomedium, "success_ratio_rx").text = str(success_ratio_rx)
    
    events = ET.SubElement(simulation, "events")
    ET.SubElement(events, "logoutput").text = "40000"
    
    motetype = ET.SubElement(simulation, "motetype")
    motetype.text = "org.contikios.cooja.motes.ImportAppMoteType"
    
    ET.SubElement(motetype, "identifier").text = "apptype64829377"
    ET.SubElement(motetype, "description").text = "Java Mote"
    ET.SubElement(motetype, "motepath").text = "[COOJA_DIR]/build/classes/java/main"
    ET.SubElement(motetype, "moteclass").text = "org.contikios.cooja.motes.Peer2PeerMote"
    
    mote_id = 1
    for k in range(layers):
        for i in range(rows):
            for j in range(cols):
                mote = ET.SubElement(motetype, "mote")
                
                interface_config_id = ET.SubElement(mote, "interface_config")
                interface_config_id.text = "org.contikios.cooja.motes.AbstractApplicationMoteType$SimpleMoteID"
                ET.SubElement(interface_config_id, "id").text = str(mote_id)
                
                interface_config_pos = ET.SubElement(mote, "interface_config")
                interface_config_pos.text = "org.contikios.cooja.interfaces.Position"
                ET.SubElement(interface_config_pos, "pos", x=str(j * spacing_x), y=str(i * spacing_y), z=str(k * spacing_z))
                
                mote_id += 1
    
    plugins = [
        {
            "name": "org.contikios.cooja.plugins.Visualizer",
            "plugin_config": {
                "moterelations": "true",
                "skin": [
                    "org.contikios.cooja.plugins.skins.IDVisualizerSkin",
                    "org.contikios.cooja.plugins.skins.GridVisualizerSkin",
                    "org.contikios.cooja.plugins.skins.TrafficVisualizerSkin",
                    "org.contikios.cooja.plugins.skins.UDGMVisualizerSkin"
                ],
                "viewport": "4.88544704914079 0.0 0.0 4.88544704914079 -54.14192546656379 118.19272539077168"
            },
            "bounds": {"x": "1", "y": "1", "height": "400", "width": "400", "z": "2"}
        },
        {
            "name": "org.contikios.cooja.plugins.LogListener",
            "plugin_config": {
                "filter": "",
                "formatted_time": "",
                "coloring": ""
            },
            "bounds": {"x": "400", "y": "160", "height": "900", "width": "1320", "z": "1"}
        },
        {
            "name": "org.contikios.cooja.plugins.TimeLine",
            "plugin_config": {
                "mote": ["0", "1", "2"],
                "showRadioRXTX": "",
                "showRadioHW": "",
                "showLEDs": "",
                "zoomfactor": "500.0"
            },
            "bounds": {"x": "0", "y": "1859", "height": "166", "width": "1720", "z": "4"}
        },
        {
            "name": "org.contikios.cooja.plugins.Notes",
            "plugin_config": {
                "notes": "Enter notes here",
                "decorations": "true"
            },
            "bounds": {"x": "400", "y": "0", "height": "160", "width": "1320", "z": "3"}
        },
        {
            "name": "org.contikios.cooja.plugins.ScriptRunner",
            "plugin_config": {
                "scriptfile": "[COOJA_DIR]/headless_logger.js",
                "active": "true"
            },
            "bounds": {"x": "400", "y": "1060", "height": "700", "width": "1320"}
        }
    ]
    
    for plugin in plugins:
        plugin_element = ET.SubElement(simconf, "plugin")
        plugin_element.text = plugin["name"]
        plugin_config = ET.SubElement(plugin_element, "plugin_config")
        for key, value in plugin["plugin_config"].items():
            if isinstance(value, list):
                for item in value:
                    ET.SubElement(plugin_config, key).text = item
            else:
                ET.SubElement(plugin_config, key).text = value
        bounds = ET.SubElement(plugin_element, "bounds")
        for key, value in plugin["bounds"].items():
            bounds.set(key, value)
    
    pretty_xml = prettify(simconf)
    filename = f"../simulations/java_{rows}x{cols}x{layers}.csc"
    with open(filename, "w") as f:
        f.write(pretty_xml)


if __name__ == "__main__":
    create_simulation_xml(
        rows=4, 
        cols=3,
        layers=1,
        spacing_x=3, 
        spacing_y=12, 
        spacing_z=5,
        tx_range=14, 
        interference_range=20, 
        success_ratio_tx=0.9, 
        success_ratio_rx=0.9
    )
