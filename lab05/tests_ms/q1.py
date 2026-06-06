test = {
  'name': 'Question 1',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
            'code': r"""
             >>> # Need to define your name at top of sheet
             >>> type(name) == str
             True
             >>> len(name.split('.')) != 4
             True
             """
        },

        {
          'code': r"""
          >>> number_strawberry == 3
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