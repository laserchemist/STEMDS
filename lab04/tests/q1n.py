test = {
  'name': 'Question 2',
  'points': 1,
  'suites': [
    {
      'cases': [

        {
            'code': r"""
            >>> import numpy as np
            >>> np.mean(weights) == 1690
            True
            >>> round(np.std(weights), 0) == 2215
            True
            >>> len(weights) == 5
            True
            """
        },
      ],
      'scored': True,
      'setup': '',
      'teardown': '',
      'type': 'doctest'
   }
  ]
}