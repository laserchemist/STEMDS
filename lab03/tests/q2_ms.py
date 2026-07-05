test = {
  'name': 'Question 2',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(top_games) == tables.Table
          True
          >>> top_games.select('Game', 'Sales (millions)').sort('Game')
          Game             | Sales (millions)
          GTA V            | 185
          Human Fall Flat  | 40
          Mario Kart 8     | 61
          Minecraft        | 238
          PUBG             | 75
          Pokémon Red/Blue | 37
          Red Dead 2       | 57
          Terraria         | 44.5
          Tetris           | 100
          Wii Sports       | 82.9
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
