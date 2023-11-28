# befx

Execute [Befunge][befunge] code. "beef-ex".

![demo image](demo.gif)

## what

This is a mostly complete Befunge-93 interpreter! Befunge is an esoteric language that executes in two dimensions!

## usage

### Run with visualization

```
python befx.py examples/helloworld.befunge
```

### Run faster

```
python befx.py -f 100 examples/helloworld.befunge
```

### Headless mode; no visualization or delays

```
python befx.py -H examples/helloworld.befunge
```

### Piped input

```
echo -e "3\n6\n7\n0\n" | python befx.py examples/calculator.befunge -H
```

## as a library

Probably don't do this, but if you insist:

```python
from befx import exec_befunge

output = exec_befunge('"!dlroW olleH">:#,_@')
print(output)
```

[befunge]: https://esolangs.org/wiki/Befunge
