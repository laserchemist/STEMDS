test = {
  'name': 'Question 10',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> super_strong.num_rows == 3 or super_strong.num_rows == 4
          True
          >>> np.count_nonzero(super_strong.column('Strength') > 1900) == super_strong.num_rows
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
