test = {
  'name': '12',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> import numpy as np
          >>> type(interesting_array) == np.ndarray
          True
          >>> type(interesting_list) == list
          True
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> len(interesting_array)
          5
          >>> len(interesting_list)
          5
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> import numpy as np
          >>> sum(interesting_array == np.array([0, 1, -1, math.pi, math.e]))
          5
          >>> interesting_list == [0, 1, -1, math.pi, math.e]
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
