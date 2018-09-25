beetagg
=======

**beetagg** is a Python library to detect and parse Beetaggs. It includes a detector (based on OpenCV) as well as an interface to query the backend servers.


Getting Started
---------------

Fetch and install the library:
```bash
$ pip install git+https://github.com/george-hopkins/beetagg
```

Decode images in a single line:
```python
from beetagg import detect

print(detect('yourcode.jpg'))
```

In addition, the library contains a built-in commandline interface:
```bash
$ beetagg yourcode.jpg
CODE
123123
$ beetagg yourcode.jpg --resolve
Example Inc.
[1] Website
$ beetagg yourcode.jpg --resolve 1
https://www.example.com
```


Disclaimer
----------
This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Connvision AG or any of its affiliates or subsidiaries.
