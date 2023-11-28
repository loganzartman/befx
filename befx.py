#! /usr/bin/python3

import sys
from dataclasses import dataclass
from enum import Enum
from random import choice
from time import sleep
import term

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
  stringmode: bool
  output: list[str]

  def push(self, val: int):
    self.stack.append(val)

  def pop(self):
    if not len(self.stack):
      return 0
    return self.stack.pop()
  
  def get_output(self):
    return "".join(self.output)

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
    direction=Direction.RIGHT,
    stringmode=False,
    output=[]
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
  if state.stringmode and c != '"':
    state.push(ord(c))
    return

  if c == '+':
    a = state.pop() 
    b = state.pop() 
    state.stack.append(a + b)
  elif c == '-':
    a = state.pop() 
    b = state.pop() 
    state.stack.append(b - a)
  elif c == '*':
    a = state.pop() 
    b = state.pop() 
    state.stack.append(a * b)
  elif c == '/':
    a = state.pop()
    b = state.pop()
    if a == 0:
      raise Exception('Computing b/a where a=0; what result do you want?') 
    state.stack.append(b // a)
  elif c == '%':
    a = state.pop()
    b = state.pop()
    if a == 0:
      raise Exception('Computing b%a where a=0; what result do you want?') 
    state.stack.append(b % a)
  elif c == '!':
    a = state.pop()
    if a == 0:
      state.stack.append(1)
    else:
      state.stack.append(0)
  elif c == '`':
    a = state.pop()
    b = state.pop()
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
    a = state.pop()
    if a == 0:
      state.direction = Direction.RIGHT
    else:
      state.direction = Direction.LEFT
  elif c == '|':
    a = state.pop()
    if a == 0:
      state.direction = Direction.DOWN
    else:
      state.direction = Direction.UP
  elif c == '"':
    state.stringmode = not state.stringmode
  elif c == ':':
    a = state.pop()
    state.push(a)
    state.push(a)
  elif c == '\\':
    a = state.pop()
    b = state.pop()
    state.stack.append(a)
    state.stack.append(b)
  elif c == '$':
    state.pop()
  elif c == '.':
    a = state.pop()
    state.output.append(str(a))
  elif c == ',':
    a = state.pop()
    state.output.append(chr(a))
  elif c == '#':
    step_pc(state)
  elif c == 'g':
    raise NotImplementedError()
  elif c == 'p':
    raise NotImplementedError()
  elif c == '&':
    while True:
      try:
        val = int(read_input(state, "Input integer > "))
        state.stack.append(val)
        break
      except ValueError:
        print("Invalid input")
  elif c == '~':
    while True:
      char = read_input(state, "Input character > ")
      if len(char) == 1:
        state.stack.append(ord(char))
      print("Invalid input")
  elif c == '@':
    raise ExitProgram()
  elif '0' <= c <= '9':
    state.stack.append(int(c))

def step_state(state: State):
  x, y = state.pc
  c = state.program[x, y]
  execute_instruction(state, c)
  step_pc(state)

def read_input(state: State, prompt: str):
  term.savecursor()
  term.moveto(0, state.program.h + 2)
  term.cursor()
  term.sgr('33')
  term.flush()
  
  print(prompt, end="")
  term.sgr('0')
  term.flush()

  result = input()

  term.loadcursor()
  term.flush()
  return result

def draw_state(state: State):
  term.clear()
  term.nocursor()
  pc_x, pc_y = state.pc
  for y, line in enumerate(state.program.lines):
    for x, char in enumerate(line.ljust(state.program.w)):
      if x == pc_x and y == pc_y:
        term.sgr('30')
        term.sgr('47')
        term.write(char)
        term.sgr('0')
      else:
        term.write(char)
    term.write('\n')
  term.flush()

def start_app(state: State):
  try:
    term.alt()
    while True:
      try:
        draw_state(state)
        step_state(state)
        sleep(1/30)
      except ExitProgram:
        break
  except KeyboardInterrupt:
    term.clear()
  finally:
    term.noalt()
    term.reset()
    term.flush()
    print(state.get_output())

def main(path: str):
  with open(path, "r") as f:
    src = f.read()
    program = load_program(src)
    state = create_state(program)
    start_app(state)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("Usage: befx.py path")
    exit(-1)
  path = sys.argv[1]
  main(path)
