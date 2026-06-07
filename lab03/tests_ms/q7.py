test = {
  'name': 'Question 7',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(games_ranked) == tables.Table
          True
          >>> list(games_ranked.column('Game').take(range(3)))
          ['Minecraft', 'GTA V', 'Tetris']
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
