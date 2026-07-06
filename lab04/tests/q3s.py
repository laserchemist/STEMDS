test = {
  'name': '',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> # Make sure your function follows the correct function format/syntax, see above
          >>> callable(triangle_area)
          True
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> import random as _r
          >>> base = _r.randint(0, 100)
          >>> height = _r.randint(0, 100)
          >>> triangle_area(base, height) == base * height / 2
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
