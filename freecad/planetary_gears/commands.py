import os
import FreeCAD as App

from freecad.planetary_gears import ICONPATH
from freecad.planetary_gears.gears import PlanetaryGearSet


class PlanetaryGearCalculatorCmd:
    def GetResources(self):
        return {
                "MenuText": "New planetary gearset",
                "ToolTip": "Create a new planetary gearset",
                "Pixmap": os.path.join(ICONPATH, "Gear.svg")
        }

    def IsActive(self):
        if App.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        # container of the gearset
        gearset = App.ActiveDocument.addObject("App::Part", "GearSet")

        # parameters of the gears (what controls the gearset)
        gear_properties = gearset.newObject("App::FeaturePython", "gear_parameters")

        PlanetaryGearSet(gear_properties, gearset)

        App.ActiveDocument.recompute()