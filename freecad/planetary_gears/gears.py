from math import cos
from math import sin
from math import pi
import FreeCAD as App
import FreeCADGui as Gui

from freecad.gears.commands import CreateInvoluteGear
from freecad.gears.commands import CreateInternalInvoluteGear


class PlanetaryGearSet:
    gear_names = ("sun", "planet", "ring")
    passthrough_params = (
        "module",
        "beta",
        "double_helix",
        "pressure_angle",
        "height",
        "clearance",
        "backlash",
    )

    def __init__(self, obj, gearset):
        self.add_gearset_properties(obj)
        self.add_ring_properties(obj)
        self.add_sun_properties(obj)
        self.add_planet_properties(obj)
        self.add_computed_properties(obj)
        self.add_link_properties(obj, gearset)

        # self.update_gears_teeth(obj)

        # Creating the actual gears
        self.create_ring_gear(obj)
        self.create_sun_gear(obj)
        self.create_planet_gear(obj)
        self.add_gear_expressions(obj)

        obj.Proxy = self

    def add_gearset_properties(self, obj):
        obj.addProperty("App::PropertyEnumeration", "solve_for", "gearset_properties", "Choose between: planet, sun, ring")
        obj.solve_for = ["planet", "sun", "ring"]
        obj.solve_for = "ring"
        obj.addProperty("App::PropertyAngle", "beta", "gearset_properties")
        obj.beta = 0
        obj.addProperty("App::PropertyBool", "double_helix", "gearset_properties")
        obj.double_helix = False
        obj.addProperty("App::PropertyFloat", "module", "gearset_properties")
        obj.module = 1
        obj.addProperty("App::PropertyAngle", "pressure_angle", "gearset_properties")
        obj.pressure_angle = 20
        obj.addProperty("App::PropertyInteger", "planet_number", "gearset_properties")
        obj.planet_number = 5
        obj.addProperty("App::PropertyFloat", "height", "gearset_properties")
        obj.height = 5
        obj.addProperty("App::PropertyFloat", "clearance", "gearset_properties")
        obj.clearance = 0.25
        obj.addProperty("App::PropertyFloat", "backlash", "gearset_properties")
        obj.backlash = 0.1

    def add_ring_properties(self, obj):
        obj.addProperty("App::PropertyInteger", "ring_teeth", "ring_properties")
        obj.ring_teeth = 53
        obj.addProperty("App::PropertyAngle", "ring_angle", "ring_properties")
        obj.ring_angle = 0
        obj.addProperty("App::PropertyLinkHidden", "ring_gear", "ring_properties", "", 4)

    def add_sun_properties(self, obj):
        obj.addProperty("App::PropertyInteger", "sun_teeth", "sun_properties")
        obj.sun_teeth = 17
        obj.addProperty("App::PropertyAngle", "sun_angle", "sun_properties")
        obj.sun_angle = 0
        obj.addProperty("App::PropertyLinkHidden", "sun_gear", "sun_properties", "", 4)

    def add_planet_properties(self, obj):
        obj.addProperty("App::PropertyInteger", "planet_teeth", "planet_properties")
        obj.planet_teeth = 18
        obj.addProperty("App::PropertyLinkHidden", "planet_gear", "planet_properties", "", 4)

    def add_computed_properties(self, obj):
        obj.addProperty("App::PropertyFloat", "sun_dw", "computed", "", 4)
        obj.setExpression("sun_dw", "module * sun_teeth")

        obj.addProperty("App::PropertyFloat", "ring_dw", "computed", "", 4)
        obj.setExpression("ring_dw", "module * ring_teeth")

        obj.addProperty("App::PropertyFloat", "planet_dw", "computed", "", 4)
        obj.setExpression("planet_dw", "module * planet_teeth")
    
    def add_link_properties(self, obj, gearset):
        obj.addProperty("App::PropertyLinkHidden", "gearset", "links", "", 4)
        obj.gearset = gearset
        obj.addProperty("App::PropertyLinkHidden", "gears_group", "links", "", 4)
        obj.gears_group = obj.gearset.newObject("App::DocumentObjectGroup", "Gears")
        obj.addProperty("App::PropertyLinkHidden", "planets_group", "links", "", 4)
        obj.planets_group = obj.gearset.newObject("App::DocumentObjectGroup", "Planets")

    def create_ring_gear(self, obj):
        ring_gear_body = obj.gears_group.newObject("PartDesign::Body", "ring_gear")
        ring_gear_body.Visibility = False
        ring_gear_body.newObject("PartDesign::CoordinateSystem", "Center")
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", ring_gear_body)
        obj.ring_gear = CreateInternalInvoluteGear.create()
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", None)
        # gear parameters

        # now add the link object which is shown in the "assembly" of the gearset
        ring_link = obj.gearset.newObject("App::Link", "ring")
        ring_link.setLink(ring_gear_body)
        ring_link.setExpression("Placement.Rotation.Yaw", f"<<{obj.Name}>>.ring_angle")

    def create_sun_gear(self, obj):
        sun_gear_body = obj.gears_group.newObject("PartDesign::Body", "sun_gear")
        sun_gear_body.Visibility = False
        sun_gear_body.newObject("PartDesign::CoordinateSystem", "Center")
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", sun_gear_body)
        obj.sun_gear = CreateInvoluteGear.create()
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", None)

        # link sun gear
        sun_link = obj.gearset.newObject("App::Link", "sun")
        sun_link.setLink(sun_gear_body)
        sun_link.setExpression("Placement.Rotation.Yaw", f"<<{obj.Name}>>.sun_angle")

    def create_planet_gear(self, obj):
        planet_gear_body = obj.gears_group.newObject("PartDesign::Body", "planet_gear")
        planet_gear_body.Visibility = False
        planet_gear_body.newObject("PartDesign::CoordinateSystem", "Center")
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", planet_gear_body)
        obj.planet_gear = CreateInvoluteGear.create()
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", None)

    def add_gear_expressions(self, obj):
        for param in self.passthrough_params:
            for gear_name in self.gear_names:
                gear = getattr(obj, f"{gear_name}_gear")
                gear.setExpression(param,  f"<<{obj.Name}>>.{param}")
                gear.setExpression("teeth", f"<<{obj.Name}>>.{gear_name}_teeth")

        # sun beta has to be negative
        obj.sun_gear.setExpression("beta", f"-<<{obj.Name}>>.beta")

    def update_gears_teeth(self, obj):
        for prop in ("planet_teeth", "sun_teeth", "ring_teeth"):
            obj.setEditorMode(prop, 0)
        obj.setEditorMode(f"{obj.solve_for}_teeth", 1)

        if obj.solve_for == "planet":
            planet_teeth = (obj.ring_teeth - obj.sun_teeth)/2

            if planet_teeth.is_integer() is False:
                App.Console.PrintMessage("This configuration of sun and ring gears is not allowed")
            else:
                obj.planet_teeth = int(planet_teeth)
        elif obj.solve_for == "sun":
            obj.sun_teeth = obj.ring_teeth - 2*obj.planet_teeth
        elif obj.solve_for == "ring":
            obj.ring_teeth = obj.sun_teeth + 2*obj.planet_teeth

    def update_planets_placements(self, obj):
        planet_n = obj.planet_number
        planetCenterDistance = (obj.planet_dw + obj.sun_dw)/2
        ringPlanetRatio = obj.ring_teeth / obj.planet_teeth
        theta_0 = 180/(obj.ring_teeth + obj.sun_teeth)*(2 - (obj.planet_teeth + 1) % 2)
        transmissionRatio = obj.ring_teeth/obj.sun_teeth + 1
        theta = theta_0 + float(obj.sun_angle - obj.ring_angle) / transmissionRatio
        n = 180 / (2*theta_0*planet_n)
        
        while len(obj.planets_group.Group) < planet_n:
            # there are less links than needed, add extra
            obj.planets_group.newObject("App::Link", "planet")
        
        for i in range(planet_n, len(obj.planets_group.Group)):
            # hide extra planets; If we remove them, and then try to increase
            # the amount of planets again - they won't be re-added.
            # I don't know why, but I've already spent weeks trying to fix this, so screw it.
            obj.planets_group.Group[i].Visibility = False

        for i in range(planet_n):
            # update planet position factors to try to put all the planets
            # around the sun
            planet_pos = int(n*i)
            angle = pi/180*(theta + float(obj.ring_angle) + 4 * theta_0 * planet_pos)
            planet = obj.planets_group.Group[i]

            planet.Visibility = True
            planet.setLink(obj.planet_gear)
            planet.Placement.Base.x = planetCenterDistance * cos(angle)
            planet.Placement.Base.y = planetCenterDistance * sin(angle)
            planet.Placement.Rotation.Yaw = theta * (1 - ringPlanetRatio) + float(obj.ring_angle)

    def execute(self, obj):
        print(f"Execute started; planets group size: {len(obj.planets_group.Group)}")
        self.update_gears_teeth(obj)
        self.update_planets_placements(obj)
        print(f"Execute done; planets group size: {len(obj.planets_group.Group)}")

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
