#! /usr/bin/python3

import sys
from dataclasses import dataclass
from enum import Enum
from random import choice

class ExitProgram(Exception):
  pass

@dataclass
class Program:
  lines: list[str]
  w: int
  h: int
  
  def __getitem__(self, index: tuple[int, int]):
    x, y = index
    if 0 <= y < self.h:
      if 0 <= x < self.w:
        line = self.lines[y]
        if x < len(line):
          return line[x]
        return ' '
    raise Exception(f'Index out of bounds: {index}')

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

def load_program(src: str):
  lines = src.splitlines()
  w = max((len(line) for line in lines), default=0)
  h = len(lines)
  return Program(lines=lines, w=w, h=h)

def create_state(program: Program):
  return State(
    program=program, 
    stack=[], 
    pc=(0, 0), 
    direction=Direction.RIGHT
  )

def step_pc(state: State):
  x, y = state.pc
  if state.direction == Direction.RIGHT:
    x += 1
  if state.direction == Direction.DOWN:
    y += 1
  if state.direction == Direction.LEFT:
    x -= 1
  if state.direction == Direction.UP:
    y -= 1
  state.pc = (x % state.program.w, y % state.program.h)

def execute_instruction(state: State, c: str):
  if c == '+':
    a = state.stack.pop() 
    b = state.stack.pop() 
    state.stack.append(a + b)
  elif c == '-':
    a = state.stack.pop() 
    b = state.stack.pop() 
    state.stack.append(b - a)
  elif c == '*':
    a = state.stack.pop() 
    b = state.stack.pop() 
    state.stack.append(a * b)
  elif c == '/':
    a = state.stack.pop()
    b = state.stack.pop()
    if a == 0:
      raise Exception('Computing b/a where a=0; what result do you want?') 
    state.stack.append(b // a)
  elif c == '%':
    a = state.stack.pop()
    b = state.stack.pop()
    if a == 0:
      raise Exception('Computing b%a where a=0; what result do you want?') 
    state.stack.append(b % a)
  elif c == '!':
    a = state.stack.pop()
    if a == 0:
      state.stack.append(1)
    else:
      state.stack.append(0)
  elif c == '`':
    a = state.stack.pop()
    b = state.stack.pop()
    if b > a:
      state.stack.append(1)
    else:
      state.stack.append(0)
  elif c == '>':
    state.direction = Direction.RIGHT
  elif c == 'v':
    state.direction = Direction.DOWN
  elif c == '<':
    state.direction = Direction.LEFT
  elif c == '^':
    state.direction = Direction.UP
  elif c == '?':
    state.direction = choice([d for d in Direction])
  elif c == '_':
    a = state.stack.pop()
    if a == 0:
      state.direction = Direction.RIGHT
    else:
      state.direction = Direction.LEFT
  elif c == '|':
    a = state.stack.pop()
    if a == 0:
      state.direction = Direction.DOWN
    else:
      state.direction = Direction.UP
  elif c == '"':
    raise NotImplementedError()
  elif c == ':':
    state.stack.append(state.stack[-1])
  elif c == '\\':
    a = state.stack.pop()
    b = state.stack.pop()
    state.stack.append(a)
    state.stack.append(b)
  elif c == '$':
    state.stack.pop()
  elif c == '.':
    a = state.stack.pop()
    sys.stderr.write(str(a))
  elif c == ',':
    a = state.stack.pop()
    sys.stderr.write(chr(a))
  elif c == '#':
    step_pc(state)
  elif c == 'g':
    raise NotImplementedError()
  elif c == 'p':
    raise NotImplementedError()
  elif c == '&':
    raise NotImplementedError()
  elif c == '@':
    raise ExitProgram()
  elif '0' <= c <= '9':
    state.stack.append(int(c))

def step_state(state: State):
  x, y = state.pc
  c = state.program[x, y]
  execute_instruction(state, c)
  step_pc(state)

def create_app(state: State):
  from termpixels import App, Buffer, Color
  a = App()

  @a.on("frame")
  def frame():
    try:
      step_state(state)
    except ExitProgram:
      a.stop()
    
    a.screen.clear()
    for i, line in enumerate(state.program.lines):
      a.screen.print(line, 0, i)
    x, y = state.pc
    a.screen[x, y].bg = Color.rgb(1,1,1)
    a.screen[x, y].fg = Color.rgb(0,0,0)
    a.screen.update()

  return a

def main(path: str):
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
