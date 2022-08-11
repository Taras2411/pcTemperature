
from operator import index
from fastapi import FastAPI
import clr
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
clr.AddReference('OpenHardwareMonitorLib')
from OpenHardwareMonitor.Hardware import Computer
c = Computer()
c.CPUEnabled = True  # get the Info about CPU
# gpu
c.GPUEnabled = True  # get the Info about GPU
c.Open()


class CPU(BaseModel):
    amountOfCores: int = 0
    avarageTemperature: float = 0
    avarageLoad:float = 0
    allCores = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        c.Hardware[0].Update()
        for i in c.Hardware[0].Sensors:
            if "clock" in str(i.Identifier):
                self.amountOfCores += 1
        self.amountOfCores -=1
        for i in range(0, self.amountOfCores):
            newCore = CPUcore(index=i, temperature=0, load=0, frequency=0)
            newCore.update()
            self.allCores.append(newCore)
            self.avarageTemperature = self.getAvarageTemperature()
            self.avarageLoad = self.getAvarageLoad()


    def update(self):
        for i in self.allCores:
            i.update()
            self.avarageTemperature = self.getAvarageTemperature()
            self.avarageLoad = self.getAvarageLoad()
    def getAvarageTemperature(self):
        avarage = 0
        for i in self.allCores:
            avarage += i.temperature
        return avarage / self.amountOfCores
    def getAvarageLoad(self):
        avarage = 0
        for i in self.allCores:
            avarage += i.load
        return avarage / self.amountOfCores
class CPUcore (BaseModel):
    index: int
    temperature: float
    load: float
    frequency: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update()

    def update(self):
        c.Hardware[0].Update()
        for i in c.Hardware[0].Sensors:
            if f"temperature/{self.index+1}" in str(i.Identifier):
                self.temperature = i.Value
            if f"load/{self.index+1}" in str(i.Identifier):
                self.load = i.Value
            if f"clock/{self.index+1}" in str(i.Identifier):
                self.frequency = i.Value
class GPU(BaseModel):
    temperature = 0
    fanRPM = 0
    load = 0
    gpuClock = 0
    memoryClock = 0
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update()
    def update(self):
        c.Hardware[1].Update()
        for i in c.Hardware[1].Sensors:
            if "temperature" in str(i.Identifier):
                self.temperature = i.Value
            if "fan" in str(i.Identifier):
                self.fanRPM = i.Value
            if "load" in str(i.Identifier):
                self.load = i.Value
            if "clock/0" in str(i.Identifier):
                self.gpuClock = i.Value
            if "clock/1" in str(i.Identifier):
                self.memoryClock = i.Value
            if "memory" in str(i.Identifier):
                self.memoryClock = i.Value



cpu = CPU()
gpu = GPU()

@app.get("/cpu/{core_id}")
def getCore(core_id: int):
    core = cpu.allCores[core_id]
    core.update()
    encoded = jsonable_encoder(core)
    return JSONResponse(content=encoded)
@app.get("/cpu")
def getCPU():
    cpu.update()
    encoded = jsonable_encoder(cpu)
    return JSONResponse(content=encoded)

@app.get("/gpu")
def getGPU():
    gpu.update()
    encoded = jsonable_encoder(gpu)
    return JSONResponse(content=encoded)

# for z in c.Hardware[1].Sensors:
#     print(z.Identifier, z.Value)

