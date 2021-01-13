import appdaemon.plugins.hass.hassapi as hass

class DoorLight(hass.Hass):
    def initialize(self):

        self.timer = None
        self.activated = False
        self.device = self.args["toggle_entity"]

        if "door_sensor" in self.args:
            for sensor in self.split_device_list(self.args["door_sensor"]):
                self.listen_state(self.state_change, sensor)

    def state_change(self, entity, attribute, old, new, kwargs):
        # Cancel turn_off timer if there is one upon state change
        if self.timer != None:
            self.cancel_timer(self.timer)
            self.log("Cancelled off: " + self.timer)
            self.timer = None

        # If entity off, turn it on and store a variable to let us know we did it
        if self.get_state(self.device) == "off":
            self.log("Turning " + self.device + " On")
            self.turn_on(self.device)
            self.activated = True

        # When a door closes and we'd previously turned an entity on, schedule a turn_off
        if (old in ["on", "open"]) and (new in ["off", "closed"]) and self.activated:
            self.timer = self.run_in(self.light_off, self.args["time_on"], device=self.device)
            self.log("Scheduled off: " + self.timer)

    def light_off(self, args):
        self.activated = False
        self.timer = None
        self.log("Turning " + self.device + " Off")
        self.turn_off(self.device)