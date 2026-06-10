test = {
  'name': '12',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> # Your index is too high!
          >>> import math
          >>> pi == math.e
          False
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> # Your index is too low.
          >>> pi == 1 or pi == 0
          False
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> # Index start at 0, so count from 0 instead of 1
          >>> pi == -1
          False
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> import math
          >>> pi == math.pi
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
