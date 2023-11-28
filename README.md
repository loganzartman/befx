# befx

Execute [Befunge][befunge] code. "beef-ex".

![demo image](demo.gif)

## what

This is a mostly complete Befunge-93 interpreter! Befunge is an esoteric language that executes in two dimensions!

## usage

Run with visualization:

```
python befx.py examples/helloworld.befunge
```

Run faster:

```
python befx.py -f 100 examples/helloworld.befunge
```

Headless mode; no visualization:

```
python befx.py -H examples/helloworld.befunge
```

## as a library

Probably don't do this, but if you insist:

```python
from befx import exec_befunge

exec_befunge('"!dlroW olleH">:#,_@')
```

[befunge]: https://esolangs.org/wiki/Befunge
