test = {
  'name': 'Questions 5',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(seven_heroes) == Table
          True
          >>> seven_heroes.num_rows
          7
          >>> seven_heroes.take([0, 1, 2, 4, 5, 6])
          Hero            | Power          | Strength
          Spider-Man      | Wall-crawling  | 1700
          Wonder Woman    | Super strength | 2200
          Black Panther   | Vibranium suit | 2000
          Iron Man        | Powered armor  | 1900
          Thor            | Thunder god    | 3000
          Captain America | Super soldier  | 1800
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
