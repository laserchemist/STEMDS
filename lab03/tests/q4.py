test = {
  'name': 'Question 4.',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(my_record) == list
          True
          >>> type(my_record[0]) == str
          True
          >>> type(my_record[1]) == str
          True
          >>> type(my_record[2]) == float or type(my_record[2]) == int
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
