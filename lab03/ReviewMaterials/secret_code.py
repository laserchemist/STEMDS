test = {
  'name': 'secret code',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> ### By the way, this python test thing will NOT contain any hints to the code itself. Can't make it too easy!
          >>> test_open('All we do now is built upon the feats of the past.', notebook, 5)==1
          True
          """,
          'hidden': False,
          'locked': False
        }
      ],
      'scored': True,
      'setup': '',
      'teardown': print('Thank you very much for doing the Review! Your guess has been logged.'),
      'type': 'doctest'
    }
  ]
}