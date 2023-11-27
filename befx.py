#! /usr/bin/python3

import sys
from dataclasses import dataclass
from enum import Enum

@dataclass
class Program:
  lines: list[str]
  w: int
  h: int
  
  def __getitem__(self, index):
    x, y = index
    if 0 <= y < self.h:
      if 0 <= x < self.w:
        line = self.lines[y]
        if x < len(line):
          return line[x]
        return ' '
    raise Error(f'Index out of bounds: {index}')

class Direction(Enum):
  RIGHT = 0
  DOWN = 1
  LEFT = 2
  UP = 3

@dataclass
class State:
  program: Program
  stack: list[int]
  pc: tuple[int, int]
  direction: Direction

def load_program(src):
  lines = src.splitlines()
  w = max((len(line) for line in lines), default=0)
  h = len(lines)
  return Program(lines=lines, w=w, h=h)

def create_state(program):
  return State(
    program=program, 
    stack=[], 
    pc=[0, 0], 
    direction=Direction.RIGHT
  )

def step_pc(state):
  x, y = state.pc
  if state.direction == Direction.RIGHT:
    x += 1
  if state.direction == Direction.DOWN:
    y += 1
  if state.direction == Direction.LEFT:
    x -= 1
  if state.direction == Direction.UP:
    y -= 1
  state.pc = [x, y]

def step_state(state):
  x, y = state.pc
  c = state.program[x, y]
  
  if c == '>':
    state.direction = Direction.RIGHT
  elif c == 'v':
    state.direction = Direction.DOWN
  elif c == '<':
    state.direction = Direction.LEFT
  elif c == '^':
    state.direction = Direction.UP

  step_pc(state)

def create_app(state):
  from termpixels import App, Buffer, Color
  a = App()

  @a.on("frame")
  def frame():
    step_state(state)
    a.screen.clear()
    for i, line in enumerate(state.program.lines):
      a.screen.print(line, 0, i)
    x, y = state.pc
    a.screen[x, y].bg = Color.rgb(1,1,1)
    a.screen[x, y].fg = Color.rgb(0,0,0)
    a.screen.update()

  return a

def main(path):
  with open(path, "r") as f:
    src = f.read()
    program = load_program(src)
    state = create_state(program)
    create_app(state).run()

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("Usage: befx.py path")
    exit(-1)
  path = sys.argv[1]
  main(path)
