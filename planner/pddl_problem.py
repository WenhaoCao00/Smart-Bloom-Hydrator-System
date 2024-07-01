from py2pddl import goal, init

from pddl_domain import SmartBloomSystem

class SmartBloomProblem(SmartBloomSystem):
    def __init__(self):
        super().__init__()
        self.lights = SmartBloomSystem.Light.create_objs([1], prefix="l")
        self.lightTimes = SmartBloomSystem.LightTime.create_objs([1], prefix="lt")
        self.temperatures = SmartBloomSystem.Temp.create_objs([1], prefix="t")
        self.moistures = SmartBloomSystem.Moisture.create_objs([1], prefix="m")

    @init
    def init(self):
        at = [
            # ~self.light_on(self.lights[1]), # no need to specify
            self.lightTime_is_enough(self.lightTimes[1]),
            self.moisture_is_low(self.moistures[1]),
            self.temp_is_ok(self.temperatures[1])
        ]

        return at
    
    @goal
    def goal(self):
        return [
            self.temp_is_ok(self.temperatures[1]),
            self.moisture_is_ok(self.moistures[1]),
        ]
    
if __name__ == "__main__":
    pb = SmartBloomProblem()
    pb.generate_domain_pddl()
    pb.generate_problem_pddl()