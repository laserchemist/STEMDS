test = {
  'name': 'Questions 5',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(seven_records) == Table
          True
          >>> seven_records.num_rows
          7
          >>> seven_records.take([0, 1, 2, 4, 5, 6])
          Athlete           | Event        | Record
          Usain Bolt        | 100m sprint  | 9.58
          Eliud Kipchoge    | Marathon     | 7269
          Sydney McLaughlin | 400m hurdles | 50.68
          Armand Duplantis  | Pole vault   | 6.26
          Mondo Duplantis   | High jump    | 2.45
          Ryan Crouser      | Shot put     | 23.37
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
