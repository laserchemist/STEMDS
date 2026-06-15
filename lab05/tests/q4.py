test = {
  'name': 'Question 4',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> # A result of 99 may arise because you did not consider
          >>> # Bird or Birds (capital B at start of sentence). 
          >>> birds == 99
          False
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> # You are counting words that contain bird ie. bluebird not isolated words.
          >>> birds == 208
          False
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> # You missed also counting birds in addition to bird, add an elif. 
          >>> birds == 17
          False
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> # Did you use the raw data or the cleaned data?
          >>> birds == 100
          False
          """,
          'hidden': False,
          'locked': False
        },
        {
          'code': r"""
          >>> # Hooray! This is the correct number of words.
          >>> birds == 177
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