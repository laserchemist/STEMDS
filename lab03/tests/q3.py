test = {
  'name': 'Question 3',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(spotify) == tables.Table
          True
          >>> spotify.num_rows == 50
          True
          >>> spotify.select('Track', 'Artist', 'Streams (millions)', 'Genre', 'BPM', 'Energy', 'Danceability').sort(0).take(range(5))
          Track           | Artist          | Streams (millions) | Genre | BPM  | Energy | Danceability
          About Damn Time | Lizzo           | 1128               | Pop   | 110  | 85     | 80
          Anti-Hero       | Taylor Swift    | 1546               | Pop   | 97   | 64     | 66
          Arcade          | Duncan Laurence | 1010               | Pop   | 130  | 44     | 51
          As It Was       | Harry Styles    | 2459               | Pop   | 174  | 73     | 82
          Bad Habit       | Steve Lacy      | 1187               | R&B   | 95   | 60     | 73
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
