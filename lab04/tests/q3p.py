test = {
  'name': '',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> # Make sure your function follows the correct function format/syntax, see above
          >>> callable(pythagorean)
          True
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> import random as _r
          >>> import numpy as np
          >>> a = _r.randint(0, 100)
          >>> b = _r.randint(0, 100)
          >>> pythagorean(a, b) == np.sqrt(a**2+b**2)
          True
          """,
          'hidden': False,
          'locked': False
        }
      ],
      'scored': True,
      'setup': '',
      'teardown': '',
      'type': 'doctest'
    }
  ]
}
