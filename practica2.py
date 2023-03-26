#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 17:14:33 2023

@author: lau
"""

from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Value
import time, random

NCARS = 100
NPED = 10
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0)
        self.ncars= Value('i', 0)
        self.nped= Value('i', 0)
        self.coches= Condition(self.mutex)
        self.ped= Condition(self.mutex)
        self.turn = Value('i', 0)
        self.ncars_waiting= Value('i', 0)
        self.nped_waiting= Value('i', 0)
        
    def no_ped(self):
        return self.nped.value == 0 and \
            self.ncars.value == 0 and \
            (self.turn.value == 1 or
                 self.nped_waiting.value == 0)

    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        #### código
        self.ncars_waiting.value += 1
        self.ped.wait_for(self.no_ped)
        self.ncars_waiting.value -= 1
        self.ncars.value += 1
        #### código
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        self.patata.value += 1
        #### código
        self.ncars.value -= 1
        self.turn.value = 1
        self.ped.notify()
        self.coches.notify_all()
        #### código
        self.mutex.release()
        
    def no_cars(self):
        return self.ncars.value == 0 and \
            (self.turn.value == 1 or
                 self.ncars_waiting.value == 0)

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        #### código
        self.nped_waiting.value += 1
        self.coches.wait_for(self.no_cars) 
        self.nped_waiting.value -= 1
        self.nped.value += 1
        #### código
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        #### código
        self.nped.value -= 1
        self.turn.value = 0
        if self.nped.value == 0:
            self.ped.notify()
        #### código
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.patata.value}'

def delay_car_north() -> None:
    pass

def delay_car_south() -> None:
    pass

def delay_pedestrian() -> None:
    pass

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction== 'NORTH' :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=('NORTH', TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=('SOUTH', TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
