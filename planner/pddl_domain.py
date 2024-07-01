from py2pddl import Domain, create_type
from py2pddl import predicate, action

class SmartBloomSystem(Domain):
    Light = create_type("Light")
    LightTime = create_type("LightTime")
    Temp = create_type("Temp")
    Moisture = create_type("Moisture")

    @predicate(Light)
    def light_is_on(self, l):
        """ indicates if the light is on """
    
    @predicate(Light)
    def light_is_off(self, l):
        """ indicates if the light is off """
    
    @predicate(LightTime)
    def lightTime_is_enough(self, lt):
        """If this is true, it means that the plant has already had enough light time """

    @predicate(Temp)
    def temp_is_high(self, t):
        """ indicates if the temperature is too high or not """

    @predicate(Temp)
    def temp_is_ok(self, t):
        """ indicates if the temperature is OK or not """

    @predicate(Temp)
    def temp_is_low(self, t):
        """ indicates if the temperature is too low or not """

    @predicate(Moisture)
    def moisture_is_high(self, m):
        """ indicates if the moisture is too high or not """

    @predicate(Moisture)
    def moisture_is_ok(self, m):
        """ indicates if the moisture is ok or not """

    @predicate(Moisture)
    def moisture_is_low(self, m):
        """ indicates if the moisture is too low or not """

    @action(Light, Temp)
    def light_off_1(self, l, t):
        precond = [self.light_is_on(l), self.temp_is_high(t)]
        effect = [~self.light_is_on(l), self.light_is_off(l), ~self.temp_is_high(t), self.temp_is_ok(t)]
        return precond, effect
    
    @action(Light, Temp)
    def light_off_2(self, l, t):
        precond = [self.light_is_on(l), self.temp_is_ok(t)]
        effect = [~self.light_is_on(l), self.light_is_off(l), ~self.temp_is_ok(t), self.temp_is_low(t)]
        return precond, effect
    
    @action(Light, Temp)
    def light_off_3(self, l, t):
        precond = [self.light_is_on(l), self.temp_is_low(t)]
        effect = [~self.light_is_on(l), self.light_is_off(l)]
        return precond, effect

    @action(Light, Temp)
    def light_keep_off_1(self, l, t):
        precond = [self.light_is_off(l), self.temp_is_high(t)]
        effect = [~self.temp_is_high(t), self.temp_is_ok(t)]
        return precond, effect
    
    @action(Light, Temp)
    def light_keep_off_2(self, l, t):
        precond = [self.light_is_off(l), self.temp_is_ok(t)]
        effect = [~self.temp_is_ok(t), self.temp_is_low(t)]
        return precond, effect
    
    # @action(Light, Temp)
    # def light_keep_off_3(self, l, t):
    #     precond = [self.light_is_off(l), self.temp_is_low(t)]
    #     effect = []
    #     return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_1(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_high(t), self.moisture_is_high(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.moisture_is_high(m), self.moisture_is_ok(m)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_2(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_high(t), self.moisture_is_ok(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.moisture_is_ok(m), self.moisture_is_low(m)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_3(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_high(t), self.moisture_is_low(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_4(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_ok(t), self.moisture_is_high(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.temp_is_ok(t), self.temp_is_high(t), ~self.moisture_is_high(m), self.moisture_is_ok(m)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_5(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_ok(t), self.moisture_is_ok(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.temp_is_ok(t), self.temp_is_high(t), ~self.moisture_is_ok(m), self.moisture_is_low(m)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_6(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_ok(t), self.moisture_is_low(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.temp_is_ok(t), self.temp_is_high(t)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_7(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_low(t), self.moisture_is_high(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.temp_is_low(t), self.temp_is_ok(t), ~self.moisture_is_high(m), self.moisture_is_ok(m)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_8(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_low(t), self.moisture_is_ok(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.temp_is_low(t), self.temp_is_ok(t), ~self.moisture_is_ok(m), self.moisture_is_low(m)]
        return precond, effect
    
    @action(Light, Temp, Moisture)
    def light_on_9(self, l, t, m):
        precond = [self.light_is_off(l), self.temp_is_low(t), self.moisture_is_low(m)]
        effect = [~self.light_is_off(l), self.light_is_on(l), ~self.temp_is_low(t), self.temp_is_ok(t)]
        return precond, effect
    
    # @action(Light, Moisture)
    # def water_1(self, l, m):
    #     precond = [self.moisture_is_high(m)]
    #     effect = []
    #     return precond, effect
    
    @action(Moisture)
    def water_2(self, m):
        precond = [self.moisture_is_ok(m)]
        effect = [~self.moisture_is_ok(m), self.moisture_is_high(m)]
        return precond, effect
    
    @action(Moisture)
    def water_3(self, m):
        precond = [self.moisture_is_low(m)]
        effect = [~self.moisture_is_low(m), self.moisture_is_ok(m)]
        return precond, effect
    
    # @action(Temp, Moisture)
    # def water_1(self, t, m):
    #     precond = [self.temp_is_high(t), self.moisture_is_high(m)]
    #     effect = [~self.temp_is_high(m), self.temp_is_ok(m)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_2(self, t, m):
    #     precond = [self.temp_is_high(t), self.moisture_is_ok(m)]
    #     effect = [~self.temp_is_high(m), self.temp_is_ok(m), ~self.moisture_is_ok(m), self.moisture_is_high(m)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_3(self, t, m):
    #     precond = [self.temp_is_high(t), self.moisture_is_low(m)]
    #     effect = [~self.temp_is_high(m), self.temp_is_ok(m), ~self.moisture_is_low(m), self.moisture_is_ok(m)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_4(self, t, m):
    #     precond = [self.temp_is_ok(t), self.moisture_is_high(m)]
    #     effect = [~self.temp_is_ok(t), self.temp_is_low(t)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_5(self, t, m):
    #     precond = [self.temp_is_ok(t), self.moisture_is_ok(m)]
    #     effect = [~self.temp_is_ok(t), self.temp_is_low(t), ~self.moisture_is_ok(m), self.moisture_is_high(m)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_6(self, t, m):
    #     precond = [self.temp_is_ok(t), self.moisture_is_low(m)]
    #     effect = [~self.temp_is_ok(t), self.temp_is_low(t), ~self.moisture_is_low(m), self.moisture_is_ok(m)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_7(self, t, m):
    #     precond = [self.temp_is_low(t), self.moisture_is_high(m)]
    #     effect = [self.light_is_on(l)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_8(self, t, m):
    #     precond = [self.temp_is_low(t), self.moisture_is_ok(m)]
    #     effect = [~self.moisture_is_ok(m), self.moisture_is_high(m)]
    #     return precond, effect
    
    # @action(Temp, Moisture)
    # def water_9(self, t, m):
    #     precond = [self.temp_is_low(t), self.moisture_is_low(m)]
    #     effect = [~self.moisture_is_low(m), self.moisture_is_ok(m)]
    #     return precond, effect
