test = {
  'name': 'Question 11',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(dance_floor) == tables.Table
          True
          >>> dance_floor.num_rows == 5
          True
          >>> print(dance_floor.sort(0).take(range(2)))
          Track     | Artist  | Streams (millions) | Genre     | BPM  | Energy | Danceability
          CUFF IT   | Beyoncé | 924                | Pop       | 106  | 78     | 87
          Calm Down | Rema    | 1756               | Afrobeats | 106  | 80     | 90
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
