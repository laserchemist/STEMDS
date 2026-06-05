test = {
  'name': 'Question 9',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(mega_hits) == Table
          True
          >>> mega_hits.num_rows
          36
          >>> abs(average_bpm_mega_hits - 115.08333) < 1e-5
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
